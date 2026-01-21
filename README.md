## Run
### Frontend
In web directory run command:
```sh
docker compose up
```
Then open localhost:8080 in your browser.

### Description generation
You need hugging face token to download model. Paste your token to .env file in first line after `=` symbol.

Then in model directory run command:
```sh
sh run.sh
```
After command complete new content should be visible.