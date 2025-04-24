# Stage 1: Build the Go application
FROM golang:1.24.2-alpine AS builder
# Using 1.22, adjust if you use a different Go version. Alpine is used for smaller image size.

#RUN apk add --no-cache gcc

# Set the working directory inside the container
WORKDIR /app

# Copy go module files first to leverage Docker cache
COPY go.mod go.sum ./
# Download dependencies
RUN go mod download

# Copy the rest of the application source code
COPY *.go ./

# Build the Go application
# -o server: specifies the output file name
# -ldflags "-w -s": reduces binary size (optional, removes debug info)
# CGO_ENABLED=0: build statically linked binary without C dependencies (important for scratch/alpine final images)
RUN go build -o newserver

# Stage 2: Create the final lightweight image
FROM alpine:latest
# FROM scratch # Alternative: Use scratch for an absolutely minimal image,
# but you might need to add ca-certificates if your app makes HTTPS calls.
# Alpine is often a good balance.

# Install ca-certificates in case your application needs to make HTTPS requests
# (Good practice even if not strictly needed now)
RUN apk --no-cache add ca-certificates

# Set the working directory
WORKDIR /app

# Copy only the compiled binary from the builder stage

COPY --from=builder /app/newserver . 
# Note: We do NOT copy the data.db file here. It will be managed by a Docker volume.

# Expose the port the application listens on
EXPOSE 8080

# Command to run the executable when the container starts
# The database file './data.db' will be created in the WORKDIR (/app)
CMD ["./newserver"]