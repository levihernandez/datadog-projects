# Build stage
FROM maven:3.8.5-openjdk-17 AS build

WORKDIR /app

#Uncomment to add the datadog tracing library, leave commented for auto instrumentation
#RUN curl -Lo dd-java-agent.jar https://dtdg.co/latest-java-tracer 

COPY accounts/mvnw .
COPY accounts/.mvn .mvn
COPY accounts/pom.xml .
COPY accounts/src ./src

RUN chmod +x mvnw && ./mvnw clean package -DskipTests && ls -l target/

# Final stage
FROM openjdk:17-slim

WORKDIR /app

# Copy the built jar file from the build stage
COPY --from=build /app/target/accounts-0.0.1-SNAPSHOT.jar app.jar

# Run java app, works with Datadog auto instrumentation
ENTRYPOINT ["java", "-jar", "app.jar"]

#Uncomment to run with tracing, leave commented for auto instrumentation
#ENTRYPOINT ["java" , "-javaagent:../dd-java-agent.jar", "-Ddd.trace.sample.rate=1", "-jar" , "target/notes-0.0.1-SNAPSHOT.jar"]  