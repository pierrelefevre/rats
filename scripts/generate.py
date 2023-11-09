import csv
from openai import OpenAI
from dotenv import load_dotenv
import os
import pickle
import base64

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")

client = OpenAI(api_key=OPENAI_API_KEY, organization=OPENAI_ORG_ID)


def read_txt():
    file = open('../drop/rats-with-descriptions.txt', 'r')
    lines = file.readlines()
    file.close()

    rats = []
    for i, line in enumerate(lines):
        s1 = line.split('.')
        s2 = s1[1].split('-')

        id = i + 1
        name = s2[0].strip()
        description = '-'.join(s2[1:]).strip()

        tier = "Common"
        rare = ["Netrunner Rat", "Sumo Rat", "Gangster Rat"]
        if name in rare:
            tier = "Rare"

        rat = {
            'tokenID': id,
            'name': name,
            'description': description,
            'file_name': f'{id}.png',
            'external_url': f'https://rats.casa/rat/{id}.png',
            'attributes[Tier]': tier
        }
        rats.append(rat)
    return rats


def save_csv(rats):
    with open('../drop/rats.csv', 'w', newline='') as csvfile:
        fieldnames = ['tokenID', 'name', 'description',
                      'file_name', 'external_url', 'attributes[Tier]']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for rat in rats:
            writer.writerow(rat)


def generate_image(rat):

    print(f"{rat['tokenID']} Getting prompt")
    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "user",
                "content": f"write the prompt for generating a headshot picture of a {rat['name']}, {rat['description']} background on a street of the dystopian city"}
        ]
    )

    prompt = completion.choices[0].message.content
    
    print(f"{rat['tokenID']} Getting image")
    img = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        quality="hd",
        response_format="b64_json"
    )

    print(f"{rat['tokenID']} Saving image")
    image = base64.b64decode(img.data[0].b64_json)
    with open(f"../drop/Media/{rat['tokenID']}.png", "wb") as fh:
        fh.write(image)

def find_already_generated():
    files = os.listdir('../drop/Media')
    ids = []
    for file in files:
        ids.append(int(file.split('.')[0]))
    return ids


def main():
    rats = read_txt()

    print(f'Loaded {len(rats)} rats')

    print('Exporting CSV')
    save_csv(rats)

    for rat in rats:
        if rat['tokenID'] in find_already_generated():
            continue
        try:
            generate_image(rat)
        except Exception as e:
            print(f"{rat['tokenID']} Error: {e}")




if __name__ == "__main__":
    main()
