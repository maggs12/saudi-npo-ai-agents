FROM node:20-slim

WORKDIR /app

# Install dependencies
COPY frontend/package*.json /app/
RUN npm install

# Copy application code
COPY frontend/ /app/

EXPOSE 3000

CMD ["npm", "run", "dev"]
