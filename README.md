# transcribe

whisper experiments

notes: https://docs.google.com/document/d/17_RQSM3_GgVwC3HanT350tm9OaY-WZ9K4y6ZPJfiLOc/edit

trello: https://trello.com/b/523mepi1/transcribe

# API

* Create a request to transcribe a URL: `POST /api/v1/transcribe`

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
* Get results for url: `GET /api/v1/transcription/<uuid>/details`

https://transcribe.param.codes/api/v1/transcription/331118e7-8b4a-4e7f-bfe0-0cc5cec2a974/details

http://localhost:6550/api/v1/transcription/b59803b8-ef45-47fc-9c5a-8343df208179/details


# Frontend dev

```
cd frontend
npm run dev
```
