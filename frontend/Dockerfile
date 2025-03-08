FROM node:16-alpine

WORKDIR /app

# Add package.json first for better layer caching
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Fix permissions for node user
RUN mkdir -p /app/node_modules/.cache && chmod -R 777 /app/node_modules/.cache

# Expose port 3000
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
