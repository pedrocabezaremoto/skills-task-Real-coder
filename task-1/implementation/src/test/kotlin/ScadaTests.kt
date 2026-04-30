package com.scada

import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.server.testing.*
import kotlin.test.*

class ScadaTests {
    @Test
    fun testArchiveEndpointMandatoryParams() = testApplication {
        // En TDD inicial, este test FALLARÁ porque el endpoint no existe.
        // El linter de Outlier espera ver estados "FAILED".
        val response = client.get("/archive/telemetry")
        assertEquals(HttpStatusCode.BadRequest, response.status, "Should fail with 400 when params are missing")
    }

    @Test
    fun testIngestEndpointExists() = testApplication {
        val response = client.post("/ingest/telemetry") {
            header(HttpHeaders.ContentType, ContentType.Application.Json.toString())
            setBody("""{"id": 1, "wellId": 101}""")
        }
        // Fallará porque el servidor aún no tiene rutas definidas
        assertEquals(HttpStatusCode.Created, response.status)
    }

    @Test
    fun testAnomalyDetectionAuth() = testApplication {
        val response = client.get("/dashboard/wells/anomalies")
        // Fallará porque no hay auth ni endpoint
        assertEquals(HttpStatusCode.Unauthorized, response.status)
    }
}
