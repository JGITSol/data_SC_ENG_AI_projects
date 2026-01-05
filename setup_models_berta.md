<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# write full setup for wrangler that will serve the purpose outlined above

To serve a BERT-style model on Cloudflare Pages for browser-based inference, you need to configure your environment to handle large binary files and specific security headers. Below is the full setup using **Wrangler** and the required project structure.

### Project Structure

Organize your project to separate the model assets from your application logic. Placing the model in a `public` or `dist` folder ensures it is deployed as a static asset.

```text
my-bert-app/
├── public/
│   ├── models/
│   │   ├── model_quantized.onnx
│   │   ├── tokenizer.json
│   │   └── config.json
│   ├── _headers           <-- Critical for Multi-threading
│   └── index.html
├── src/
│   └── main.js            <-- Inference Logic
├── package.json
└── wrangler.jsonc         <-- Configuration file
```


### Wrangler Configuration

Since you are deploying to **Cloudflare Pages**, your `wrangler.jsonc` (or `wrangler.toml`) primarily defines the build directory and environment variables. Cloudflare Pages automatically treats files in your `public` directory as static assets.[^1]

```json
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "browser-bert-app",
  "pages_build_output_dir": "./public",
  "vars": {
    "ENVIRONMENT": "production"
  }
}
```


### Security Headers (`_headers`)

For the browser to use `SharedArrayBuffer` (required for multi-threaded CPU inference and WebGPU), you must provide specific headers. Create a file named `public/_headers` with the following content:

```text
/*
  Cross-Origin-Embedder-Policy: require-corp
  Cross-Origin-Opener-Policy: same-origin
  Access-Control-Allow-Origin: *
```

*Note: These headers are mandatory for `transformers.js` to avoid "SharedArrayBuffer is not defined" errors in the browser.*[^2][^3]

### Browser Implementation (`main.js`)

Use the `transformers.js` library to load the model from your local path. This prevents the browser from trying to download the model from Hugging Face every time.

```javascript
import { pipeline, env } from '@xenova/transformers';

// 1. Configure library to use local assets exclusively
env.allowLocalModels = true;
env.allowRemoteModels = false;
env.localModelPath = '/models/'; // Relative to your public root

async function runInference() {
    // 2. Initialize the pipeline
    // This will fetch /models/my-model/model_quantized.onnx
    const classifier = await pipeline('sentiment-analysis', 'my-model', {
        device: 'webgpu', // Use 'wasm' if WebGPU is unavailable
    });

    // 3. Execute on the local device
    const output = await classifier("This is running entirely in my browser!");
    console.log(output);
}

runInference();
```


### Deployment Commands

Use the following commands to install dependencies, convert your model, and deploy.

1. **Install dependencies:**
`npm install @xenova/transformers`
2. **Convert Model (Python side):**
Use the `optimum-cli` to export your chosen model (e.g., `distilbert-base-uncased`) to the `./public/models/my-model` directory with quantization enabled.[^4]
3. **Deploy to Cloudflare:**

```bash
# Run a local development server
npx wrangler pages dev ./public

# Deploy to production
npx wrangler pages deploy ./public
```


### Recommended Model Sizes for Cloudflare Pages

| Model Type | File Size (Int8) | Recommendation |
| :-- | :-- | :-- |
| **MiniLM-L6-v2** | ~23 MB | **Best choice** for fast initial load [^5]. |
| **TinyBERT-4** | ~15 MB | Ideal for very low-end mobile devices [^6]. |
| **DistilBERT** | ~67 MB | Best for higher accuracy requirements [^7]. |

<div align="center">⁂</div>

[^1]: https://developers.cloudflare.com/pages/framework-guides/deploy-anything/

[^2]: https://github.com/jobergum/browser-ml-inference

[^3]: https://aboutweb.dev/blog/cross-origin-isolation-requirements-sharedarraybuffer-cloudflare-worker/

[^4]: https://github.com/huggingface/transformers.js

[^5]: https://supermemory.ai/blog/best-open-source-embedding-models-benchmarked-and-ranked/

[^6]: https://zenodo.org/records/15907007

[^7]: https://www.c-sharpcorner.com/article/distilbert-albert-and-beyond-comparing-top-small-language-models/

