// --- server.js ---
const express = require('express');
const path = require('path');
const app = express();
const port = 3000;

// Allow the server to read JSON data sent from Python
app.use(express.json());

// Serve the HTML file from the "public" folder
app.use(express.static(path.join(__dirname, 'public')));

// --- SERVER-SENT EVENTS (SSE) SETUP ---
let clients = [];

app.get('/live-updates', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    // Add this browser to our list of connected clients
    clients.push(res);
    
    // Remove client when they close the tab
    req.on('close', () => {
        clients = clients.filter(client => client !== res);
    });
});

// --- THE API ENDPOINT ---
// Python sends a POST request here when it sees your face/pill
app.post('/api/trigger', (req, res) => {
    const { action } = req.body;
    console.log(`Received trigger from AI: ${action}`);
    
    // Broadcast the action to the HTML webpage
    clients.forEach(client => {
        client.write(`data: ${JSON.stringify({ action })}\n\n`);
    });
    
    res.json({ success: true, message: `Action '${action}' broadcasted to UI.` });
});

app.listen(port, () => {
    console.log(`🚀 Caregiver Portal running at http://localhost:${port}`);
    console.log(`📡 API Endpoint ready at http://localhost:${port}/api/trigger`);
});