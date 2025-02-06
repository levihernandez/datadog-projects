# Use the official .NET SDK 8.0 image as the base image for building
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

# Set the working directory
WORKDIR /app

# Copy the project file and restore any dependencies
COPY PaymentProcessing/*.csproj ./
RUN dotnet restore

# Copy the rest of the application code
COPY PaymentProcessing/ ./

# Build the application
# RUN dotnet build -c Release -o out

# Build and publish a release
RUN dotnet publish -c Release -o out

# Use a lightweight .NET runtime image for the final stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime

# Set the working directory
WORKDIR /app

# Copy the built application from the build stage
COPY --from=build /app/out ./

# Expose the required ports
EXPOSE 8080

# Start your application
CMD ["dotnet", "PaymentProcessing.dll"]
