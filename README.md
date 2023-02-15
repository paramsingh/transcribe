# transcribe

whisper experiments

notes: https://docs.google.com/document/d/17_RQSM3_GgVwC3HanT350tm9OaY-WZ9K4y6ZPJfiLOc/edit

trello: https://trello.com/b/523mepi1/transcribe

# How to run

```
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

Create config file, and fill in values as needed

```
cp transcribe/config.py.sample transcribe/config.py
```

Now, run the Flask API server.

```
python -m transcribe.api
```

Run the frontend

```
cd frontend
npm install
npm run dev
```

There's background scripts that you might want to run.

```
python -m transcribe.processor.transcribe # transcribes videos
python -m transcribe.processor.improve # improves transcriptions and creates embeddings
```

# API

- Create a request to transcribe a URL: `POST /api/v1/transcribe`

Production:

```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"link":"https://www.youtube.com/watch?v=0lJKucu6HJc"}' \
  https://transcribe.param.codes/api/v1/transcribe
```

Localhost:

```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"link":"https://www.youtube.com/watch?v=0lJKucu6HJc"}' \
  http://localhost:6550/api/v1/transcribe
```

- Get results for url: `GET /api/v1/transcription/<token>/details`

https://transcribe.param.codes/api/v1/transcription/331118e7-8b4a-4e7f-bfe0-0cc5cec2a974/details

http://localhost:6550/api/v1/transcription/b59803b8-ef45-47fc-9c5a-8343df208179/details

# Frontend dev

```
cd frontend
npm run dev
```

# Run tests

First, install dev requirements.

```
pip install -r requirements_dev.txt
```

Then, just run:

```
pytest transcribe
```

**Very important:** Tests are not necessary for every single feature. Prioritize velocity over code coverage. However, we should try to keep all tests passing. `pytest transcribe` should be green.
