# Use an official Gradle image with JDK 17
FROM gradle:8.4-jdk17

# Set the working directory
WORKDIR /home/gradle/project

# Install Python (required for parsing.py)
USER root
RUN apt-get update && apt-get install -y python3 python3-pip unzip && rm -rf /var/lib/apt/lists/*
USER gradle

# Copy all files to the container
# The platform will handle the mounting, but we prepare the entry points
COPY --chown=gradle:gradle . .

# Ensure scripts are executable
RUN chmod +x run.sh

# Entry point is usually handled by the platform calling run.sh
CMD ["./run.sh"]
