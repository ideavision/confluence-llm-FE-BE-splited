# PayserAi (v0.3):
<h4>Paysera-Ai: Real-time Q/A using LLM for labeled Confluence pages & Multiple DataSources</h4>
Paysera-ai is an enterprise question-answering system that allows users to ask natural language questions against internal documents and receive reliable answers. These answers are backed by quotes and references from the source material, ensuring trustworthiness.The application aims to bridge the gap between static Confluence content and dynamic user queries. By leveraging advanced language models and vector similarity search, the application provides real-time, contextually relevant answers to user questions based on the updated content stored in Confluence.


 
Web

We use prettier for formatting. The desired version (2.8.8) will be installed via a npm i from the PayserAi/ directory. To run the formatter, use npx prettier --write . from the PayserAi/ directory. 


Next, install **Node.js** and **npm** for the frontend. After that, navigate to `PayserAi/` and run:

```bash
npm i
```

Finally, install **Playwright** (required by the Web Connector) with the Python virtual environment active:

```bash
playwright install
```

**Start the Frontend:**

   Navigate to `PayserAi/` and run:

   ```bash
   npm run dev
   ```

