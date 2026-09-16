const express = require('express');
const cors = require('cors'); // Use require to import cors
const googleTTS = require('google-tts-api');
const { TranslationServiceClient } = require('@google-cloud/translate');
const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch'); // Use require to import node-fetch
const { spawn } = require('child_process');

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

const edgeVoices = {
    'ta-male': 'ta-IN-ValluvarNeural',
    'ta-female': 'ta-IN-PallaviNeural',
    'ta-lk-male': 'ta-LK-KumarNeural',
    'ta-lk-female': 'ta-LK-SaranyaNeural',
    'ta-my-male': 'ta-MY-SuryaNeural',
    'ta-my-female': 'ta-MY-KaniNeural',
    'ta-sg-male': 'ta-SG-AnbuNeural',
    'ta-sg-female': 'ta-SG-VenbaNeural',
    'te-male': 'te-IN-MohanNeural',
    'te-female': 'te-IN-ShrutiNeural',
    'kn-male': 'kn-IN-GaganNeural',
    'kn-female': 'kn-IN-SapnaNeural',
    'ml-male': 'ml-IN-MidhunNeural',
    'ml-female': 'ml-IN-SobhanaNeural',
    'hi-male': 'hi-IN-MadhurNeural',
    'hi-female': 'hi-IN-SwararaNeural',
};

const speedMap = {
    "0.25": "-75%",
    "0.5": "-50%",
    "0.75": "-25%",
    "1": "+0%",
    "1.25": "+25%",
    "1.5": "+50%",
    "2": "+100%"
};

async function _spawnTTS(text, outputPath, voice, rate = "+0%") {
    return new Promise((resolve, reject) => {
        const py = spawn("python", ["-c", `
import asyncio, edge_tts, sys
async def main():
    communicate = edge_tts.Communicate(sys.argv[1], sys.argv[2], rate=sys.argv[4])
    await communicate.save(sys.argv[3])
asyncio.run(main())
`, text, voice, outputPath, rate]);

        let stderr = "";
        py.stderr.on("data", (d) => { stderr += d.toString(); });
        py.on("close", (code) => {
            if (code === 0 && fs.existsSync(outputPath) && fs.statSync(outputPath).size > 0) {
                resolve(outputPath);
                return;
            }
            reject(new Error(`edge-tts (voice=${voice}) failed: code=${code} ${stderr.trim().split("\\n").pop() || ""}`));
        });
        py.on("error", reject);
    });
}

async function generateEdgeTTS(text, voice, speed, audioFilePath) {
    const rate = speedMap[speed] || "+0%";
    return await _spawnTTS(text, audioFilePath, voice, rate);
}

app.post('/text-to-audio', async (req, res) => {

    const supportedVoices = {
        'en': 'en',       // English
        'es': 'es',       // Spanish
        'fr': 'fr',       // French
        'de': 'de',       // German
        'ta': 'ta',       // Tamil
        'ja': 'ja',       // Japanese
        'ko': 'ko',       // Korean
        'hi': 'hi',       // Hindi
        'zh-CN': 'zh-CN', // Chinese (Simplified)
        'ru': 'ru'        // Russian
    };

    const { text, voice = 'en', speed = 1 } = req.body;

    if (!text) {
        return res.status(400).json({ error: 'No text provided' });
    }

    // Check if it's an Edge voice first
    if (edgeVoices[voice]) {
        try {
            const audioFilePath = path.join(audioDir, 'output.mp3');
            await generateEdgeTTS(text, edgeVoices[voice], speed, audioFilePath);
            return res.sendFile(audioFilePath);
        } catch (error) {
            console.error('Edge TTS Error:', error);
            return res.status(500).json({ error: 'Failed to generate audio using Edge TTS' });
        }
    }

    // Remove '-male' or '-female' suffix before sending the request for Google TTS
    const baseVoice = voice.replace('-male', '').replace('-female', '');

    // Check if the baseVoice is supported
    if (!supportedVoices[baseVoice]) {  // Use baseVoice instead of voice here
        return res.status(400).json({ error: 'Invalid voice parameter' });
    }

    const validSpeeds = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2];

    if (!validSpeeds.includes(parseFloat(speed))) {
        return res.status(400).json({ error: 'Invalid speed parameter' });
    }

    try {
        const url = googleTTS.getAudioUrl(text, {
            lang: baseVoice,  // Use baseVoice here
            slow: speed < 1,
            host: 'https://translate.google.com',
        });

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch audio: ${response.statusText}`);
        }

        const arrayBuffer = await response.arrayBuffer();
        const buffer = Buffer.from(arrayBuffer);

        const audioFilePath = path.join(audioDir, 'output.mp3');
        fs.writeFileSync(audioFilePath, buffer);

        res.sendFile(audioFilePath);

    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Failed to translate text or generate audio' });
    }
});

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});
