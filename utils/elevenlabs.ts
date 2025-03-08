export async function generateVoice(text: string): Promise<Blob> {
  const API_KEY = process.env.NEXT_PUBLIC_ELEVENLABS_API_KEY;
  const VOICE_ID = process.env.NEXT_PUBLIC_ELEVENLABS_VOICE_ID;

  if (!API_KEY || !VOICE_ID) {
    throw new Error('ElevenLabs API key or Voice ID not configured');
  }

  const response = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`,
    {
      method: 'POST',
      headers: {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': API_KEY,
      },
      body: JSON.stringify({
        text,
        model_id: 'eleven_monolingual_v1',
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.5,
        },
      }),
    }
  );

  if (!response.ok) {
    throw new Error('Failed to generate voice');
  }

  return response.blob();
}
