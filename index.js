const express = require('express');
const cors = require('cors'); // Use require to import cors
const googleTTS = require('google-tts-api');
const { TranslationServiceClient } = require('@google-cloud/translate');
const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch'); // Use require to import node-fetch

const app = express();
const port = 3000;

// Initialize Google Cloud Translation client
const translationClient = new TranslationServiceClient();

app.use(cors()); // Use cors middleware
app.use(express.json());
app.use(express.static(path.join(__dirname))); // Serve static files from the root directory

// Ensure the 'audio' directory exists
const audioDir = path.join(__dirname, 'audio');
if (!fs.existsSync(audioDir)) {
    fs.mkdirSync(audioDir);
}

// Translate text and generate audio
app.post('/text-to-audio', async (req, res) => {
    const { text, voice = 'en', speed = 1 } = req.body;

    if (!text) {
        return res.status(400).json({ error: 'No text provided' });
    }

    // Define supported voices
    const supportedVoices = {
        'en': 'en',
        'es': 'es',
        'fr': 'fr',
        'de': 'de',
        'ta': 'ta' // Check if Tamil is supported by your library
    };

    if (!supportedVoices[voice]) {
        return res.status(400).json({ error: 'Invalid voice parameter' });
    }

    const validSpeeds = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2]; // Common speed values

    if (!validSpeeds.includes(parseFloat(speed))) {
        return res.status(400).json({ error: 'Invalid speed parameter' });
    }

    try {
        // Generate audio URL
        const url = googleTTS.getAudioUrl(text, {
            lang: voice,
            slow: speed < 1,
            host: 'https://translate.google.com',
        });

        // Download the audio file
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch audio: ${response.statusText}`);
        }

        // Convert response to buffer
        const arrayBuffer = await response.arrayBuffer();
        const buffer = Buffer.from(arrayBuffer);

        const audioFilePath = path.join(audioDir, 'output.mp3');
        fs.writeFileSync(audioFilePath, buffer);

        // Send the audio file
        res.sendFile(audioFilePath);

    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Failed to translate text or generate audio' });
    }
});

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});
