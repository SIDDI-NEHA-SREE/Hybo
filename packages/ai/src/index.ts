import { GoogleGenAI } from '@google/genai';

const apiKey = process.env.GEMINI_API_KEY || 'dummy-key';
export const ai = new GoogleGenAI({ apiKey });

export async function generateCityResponse(prompt: string) {
  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: prompt,
    config: {
      systemInstruction: "You are the HYBO Smart City assistant. Answer citizen queries concisely and professionally.",
    }
  });
  return response.text;
}
