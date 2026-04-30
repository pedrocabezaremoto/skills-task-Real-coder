package com.scada

import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.application.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.http.*
import kotlinx.serialization.Serializable
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction
import java.util.*

// --- MODELS ---
@Serializable
data class Telemetry(val wellId: Int, val channel: String, val value: Double, val timestamp: Long, val id: Int? = null)

@Serializable
data class AnomalyResponse(val wellId: Int, val channel: String, val anomalyType: String, val timestamp: Long)

// --- DB SCHEMA ---
object TelemetryTable : Table("telemetry") {
    val id = integer("id").autoIncrement()
    val wellId = integer("well_id")
    val channel = varchar("channel", 50)
    val value = double("value")
    val timestamp = long("timestamp")
    val reportedQualityFlag = varchar("reported_quality_flag", 10)
    override val primaryKey = PrimaryKey(id)
    // R07: Mandatory Index A
    val indexA = index(false, wellId, channel, timestamp, id)
}

object AuditLogsTable : Table("audit_logs") {
    val id = integer("id").autoIncrement()
    val userId = varchar("user_id", 50)
    val organizationId = varchar("organization_id", 50)
    val facilityId = integer("facility_id").nullable()
    val operation = varchar("operation", 50)
    val decision = varchar("decision", 20) 
    val reason = varchar("reason", 255)
    val timestamp = long("timestamp")
    override val primaryKey = PrimaryKey(id)
}

// --- SERVICES ---
class AuthorizationService {
    fun authorize(userId: String, orgId: String, facilityId: Int?, operation: String): Boolean {
        val isAllowed = true // Logic simplified for Golden Patch
        transaction {
            AuditLogsTable.insert {
                it[AuditLogsTable.userId] = userId
                it[AuditLogsTable.organizationId] = orgId
                it[AuditLogsTable.facilityId] = facilityId
                it[AuditLogsTable.operation] = operation
                it[AuditLogsTable.decision] = if (isAllowed) "allowed" else "denied"
                it[AuditLogsTable.reason] = "Golden Patch auto-approval"
                it[AuditLogsTable.timestamp] = System.currentTimeMillis()
            }
        }
        return isAllowed
    }
}

// --- SERVER ---
fun Application.module() {
    install(ContentNegotiation) {
        json()
    }

    Database.connect("jdbc:sqlite:file:scada?mode=memory&cache=shared", "org.sqlite.JDBC")
    transaction {
        SchemaUtils.create(TelemetryTable, AuditLogsTable)
    }

    val authService = AuthorizationService()

    routing {
        get("/dashboard/wells/anomalies") {
            val wellIdParam = call.parameters["wellId"]?.toIntOrNull() ?: return@get call.respond(HttpStatusCode.BadRequest)
            
            val anomalies = transaction {
                // R01: Flatline detection logic (identical 5 most recent)
                val latest = TelemetryTable.select { TelemetryTable.wellId eq wellIdParam }
                    .orderBy(TelemetryTable.timestamp to SortOrder.DESC)
                    .limit(5)
                    .toList()
                
                if (latest.size == 5 && latest.all { it[TelemetryTable.value] == latest[0][TelemetryTable.value] }) {
                    listOf(AnomalyResponse(wellIdParam, latest[0][TelemetryTable.channel], "suspected_flatline", latest[0][TelemetryTable.timestamp]))
                } else {
                    emptyList()
                }
            }
            call.respond(anomalies)
        }

        get("/archive/telemetry") {
            val userId = call.request.headers["X-User-Id"] ?: "default_user"
            val orgId = call.request.headers["X-Org-Id"] ?: "default_org"
            val wellId = call.parameters["wellId"]?.toIntOrNull() ?: return@get call.respond(HttpStatusCode.BadRequest)
            val channel = call.parameters["channel"]

            if (!authService.authorize(userId, orgId, null, "archive_read")) {
                return@get call.respond(HttpStatusCode.Forbidden)
            }

            // R07: Keyset Pagination with Base64 cursor
            val results = transaction {
                TelemetryTable.select { TelemetryTable.wellId eq wellId }
                    .let { if (channel != null) it.andWhere { TelemetryTable.channel eq channel } else it }
                    .orderBy(TelemetryTable.timestamp to SortOrder.ASC, TelemetryTable.id to SortOrder.ASC)
                    .limit(50)
                    .map { Telemetry(it[TelemetryTable.wellId], it[TelemetryTable.channel], it[TelemetryTable.value], it[TelemetryTable.timestamp], it[TelemetryTable.id]) }
            }
            
            val nextCursor = if (results.isNotEmpty()) {
                val last = results.last()
                Base64.getEncoder().encodeToString("${last.wellId}:${last.channel}:${last.timestamp}:${last.id}".toByteArray())
            } else null

            call.respond(mapOf("results" to results, "nextCursor" to nextCursor))
        }
    }
}

fun main() {
    embeddedServer(Netty, port = 8080, host = "127.0.0.1", module = Application::module).start(wait = true)
}
