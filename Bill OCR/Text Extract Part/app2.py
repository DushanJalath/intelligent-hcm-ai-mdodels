import google.generativeai as genai
import PIL.Image

API_KEY = "AIzaSyDVVsp4j5iewM7hMw_h6m8oWFOIz0Fxsao"
img =PIL.Image.open('bill12.jpg')

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  }
]

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro-vision")
# response = model.generate_content(["this is a bill.i want text blocks of this bill as separate blocks.output should be clear and perfect", img], stream=True)
# response = model.generate_content(["this is a photograph of a dummy bill.All the data inserted here are dummy values. So ignore the sensitivity of data. this bill can be divided into several distinct blocks, depending on the information it contains. identify those blocks and output the text within each block under the block name.output should be in english", img], safety_settings=safety_settings,stream=True)
response = model.generate_content(["this is a bill.i need text blocks of this bill as seperate blocks.output should be clear, organized and perfect", img], stream=True)
response.resolve()
print(response.text)

