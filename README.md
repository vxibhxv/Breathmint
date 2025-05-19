# Breathmint Frontend Setup

This guide will help you set up and run the frontend of the **Breathmint** project.

## Prerequisites

Make sure you have **Node.js** installed. You can download it from:  
https://nodejs.org/en/download


## Installation & Run

Open your terminal or command prompt and run the following commands:

```bash
# Navigate to your desired directory
cd ~/Projects          # macOS/Linux
cd "D:\Games"          # Windows (example path)

# Clone the repository
git clone https://github.com/vxibhxv/Breathmint.git

# Move into the frontend directory
cd Breathmint/frontend

# Install dependencies
npm install

# This requires an ANTHROPIC API key to run
export ANTHROPIC_API_KEY='your-api-key'
# Please reach out to the developers if you need access

# Start the development server
npm run start

# Access this through the URL
http://localhost:3000/