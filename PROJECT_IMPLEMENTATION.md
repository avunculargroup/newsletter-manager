Project Implementation Plan:Automated Newsletter Generation
===========================================================

1 Backgroundand motivation
--------------------------

You currently spend **~1 hour each week** researching topics,drafting text in ChatGPT, picking or creating images and transferring theresult into a Mailjet newsletter template. Even though Mailjet recentlyintroduced an AI assistant that can rewrite, translate or adjust tone ofselected text[\[1\]](https://documentation.mailjet.com/hc/en-us/articles/35526276229531-Mailjet-s-AI-Assistant#:~:text=Why Use the AI Assistant?), you still have to manually use ChatGPT, copy‑paste the result andassemble the newsletter. This process is time‑consuming and repetitive anddistracts you from more creative tasks.

Recently you noted that you are interested in using **MCP servers**such as Firecrawl (for web scraping and search) and potentially **Search1API**to gather data. MCP servers are a model‑context protocol that expose tools(functions) to AI models. For example, the Firecrawl MCP server provides webscraping with custom wait times, batch scraping, deep crawling, structured dataextraction and LLM‑powered research[\[2\]](https://portkey.ai/docs/integrations/mcp-servers/firecrawl-mcp-server#:~:text=Key features). You also prefer building the front end in **Next.js** and wouldlike to interface with large language models through **OpenRouter**, whichstandardises tool‑calling across providers and allows you to swap models easily[\[3\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=MCP servers are a popular,compatible tool calling)[\[4\]](https://openrouter.ai/docs/guides/features/tool-calling#:~:text=Tool calls ,to the user’s original question). These preferences must be factored into the design andimplementation.

The goal of this project is to build a **web application** andbackground workflow that automatically collects relevant information, uses alarge language model (LLM) to generate the newsletter text, finds suitableimages and then assembles and sends the email through the Mailjet API withoutrelying on the ChatGPT chat interface. The project will start with this singlenewsletter use‑case and be designed so more workflows can be added later.

2 Objectivesand scope
---------------------

### Objectives

·        **Automate content creation** – gather sources (e.g., curated news or blog posts) and summarise themusing LLMs. In addition to traditional APIs like **NewsAPI**, the designshould integrate **MCP servers** for web scraping and search; for example,the Firecrawl MCP server exposes tools for scraping single URLs, performingbatch scrapes, deep crawling, and LLM‑powered research[\[2\]](https://portkey.ai/docs/integrations/mcp-servers/firecrawl-mcp-server#:~:text=Key features). These sources will feed into anLLM accessed through **OpenRouter**, which standardises tool‑calling acrossproviders and allows switching models easily[\[3\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=MCP servers are a popular,compatible tool calling). Prompt templates andbrand‑voice examples will ensure the generated summaries match your style.

·        **Automate image selection** – find or generate appealing images that correspond to the stories inthe newsletter.

·        **Assemble and send emailsprogrammatically** – generate responsive HTML/MJMLtemplates, create a campaign draft via Mailjet’s /campaigndraft endpoint, add the content, test, and then schedule/send it[\[5\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#create-a-campaign-draft)[\[6\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#add-email-contents)[\[7\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#test-your-campaign)[\[8\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#send-the-campaign).

·        **Provide a simple user interface** – allow you to configure the topics for the week, review/edit thegenerated newsletter and trigger or schedule the send. Because you arecomfortable with **Next.js**, the frontend will be implemented usingNext.js. Next.js 16 includes MCP support via the next‑devtools‑mcp package[\[9\]](https://nextjs.org/docs/app/guides/mcp#:~:text=Enabling Next,Coding Agents); although not required for theinitial workflow, this opens the door to agent‑assisted development and remoteintrospection in future iterations.

·        **Design for extensibility** – while the first focus is the newsletter, the architecture shouldsupport adding new agent‑based workflows later.

### Out of scope (for thefirst iteration)

·        Complex agent‑design interfaces.

·        Deep segmentation or A/B testingof campaigns (Mailjet supports this natively and can be added later).

3 Functionalrequirements
------------------------

Requirement

Description

Content sourcing

Pull articles or news items from configurable sources. Start with **NewsAPI** or RSS feeds, but also integrate **MCP servers** such as **Firecrawl** to scrape web pages, perform batch scraping, deep crawling and even LLM‑powered research[\[2\]](https://portkey.ai/docs/integrations/mcp-servers/firecrawl-mcp-server#:~:text=Key features). Firecrawl exposes endpoints for scraping single URLs, searching the web and extracting structured data via the MCP protocol. These sources should be configurable via the UI.

Article selection

Automatically rank or filter the fetched articles. The AI edge article demonstrates using a prompt template in LangChain to extract the ten most important news items from a list[\[10\]](https://newsletter.theaiedge.io/p/deep-dive-how-to-automate-writing#:~:text=Selecting the top news). A similar approach can be used.

Summarisation and copy generation

Use a large language model (LLM) accessed through **OpenRouter**, which supports tool‑calling and model routing[\[3\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=MCP servers are a popular,compatible tool calling). Convert MCP tool definitions into OpenAI‑compatible functions so the LLM can request the Firecrawl scrape/search tools when needed[\[3\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=MCP servers are a popular,compatible tool calling). Prompt templates will enforce the newsletter’s brand voice (ChatGPT’s default tone is formal[\[1\]](https://documentation.mailjet.com/hc/en-us/articles/35526276229531-Mailjet-s-AI-Assistant#:~:text=Why Use the AI Assistant?)).

Image selection/generation

For each article or section, fetch a suitable image. Options include (1) searching **Unsplash** via its **simple JSON API** (described as easy to integrate[\[11\]](https://unsplash.com/developers#:~:text=The most powerful photo engine,in the world)), (2) generating original artwork via a stable‑diffusion service, or (3) using the image produced by the article itself. Attribution must be included for Unsplash.

Template assembly

Assemble content and images into an **MJML** or responsive HTML template. Use a base template with placeholders (title, hero image, sections, CTA) and fill it programmatically.

Mailjet integration

Create a campaign draft via POST /campaigndraft specifying locale, sender, subject and list ID[\[5\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#create-a-campaign-draft); add email content by posting to /campaigndraft/{draft\_ID}/detailcontent[\[6\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#add-email-contents); test by posting to /campaigndraft/{draft\_ID}/test[\[7\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#test-your-campaign); and send via /campaigndraft/{draft\_ID}/send[\[8\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#send-the-campaign).

Scheduling and triggering

Allow scheduling (e.g., send every Monday 10 am) and manual triggering from the web UI.

User interface

Provide a simple dashboard to configure weekly topics, view/edit the generated newsletter, preview the email and click **Send**. For the MVP this will be built with **Next.js**, leveraging its server components and API routes. Although Next.js 16 includes MCP support for coding agents[\[9\]](https://nextjs.org/docs/app/guides/mcp#:~:text=Enabling Next,Coding Agents), the UI will initially call the backend services via REST or WebSocket.

Logging and error handling

Log each step of the pipeline. Provide error notifications if an API fails (e.g., NewsAPI limits, OpenAI errors, Mailjet rejection).

Security and privacy

Store API keys securely (environment variables/Key Vault). Do not store subscriber addresses outside Mailjet. Ensure compliance with email marketing regulations (unsubscribe links and contact properties are handled by Mailjet).

4 Non‑functionalrequirements
----------------------------

·        **Reliability** – the pipeline must run weekly without manual fixes.

·        **Performance** – summarisation and image searches should complete within a fewminutes to avoid delays.

·        **Maintainability** – modular code with clear separation of concerns so new workflows canbe added.

·        **Extensibility** – adding new sources, additional workflows or segmentation shouldrequire minimal changes.

·        **Legal compliance** – respect API license terms (Unsplash images require attribution;Mailjet API terms; OpenAI usage policies) and privacy regulations.

5 High‑level system architecture
--------------------------------

1.     **Data sources and search** – gather articles via NewsAPI and RSS feeds, but also through **MCPservers**. The Firecrawl MCP server exposes tools for scraping single pages,batch scraping, deep crawling, and executing web searches[\[2\]](https://portkey.ai/docs/integrations/mcp-servers/firecrawl-mcp-server#:~:text=Key features). These tools allow the system to fetch content from arbitrary websiteswhen RSS feeds are insufficient.

2.     **LLM summarisation and selectionvia OpenRouter** – the backend uses **OpenRouter** toconnect to an LLM (e.g., GPT‑4 or Claude). OpenRouter standardises tool‑callingand allows the LLM to request external tools such as firecrawl\_scrape or firecrawl\_search by converting MCP tooldefinitions to OpenAI‑compatible functions[\[3\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=MCP servers are a popular,compatible tool calling)[\[12\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=Note that interacting with MCP,but is still somewhat complex). Prompts instruct the LLM to pick the most relevant stories andsummarise them in your brand voice[\[10\]](https://newsletter.theaiedge.io/p/deep-dive-how-to-automate-writing#:~:text=Selecting the top news).

3.     **Image selection/generation** – call the Unsplash API to search for images relevant to each section(it offers simple endpoints to search or list photos[\[11\]](https://unsplash.com/developers#:~:text=The most powerful photo engine,in the world)), or use generative services such as Stable Diffusion/DALL·E to createoriginal artwork. The LLM may propose image prompts or keywords based on thearticle summaries.

4.     **Template assembly** – a template engine (e.g., MJML + Jinja2) fills placeholders with thesummarised text, images and dynamic data such as the date. The result iscompiled into HTML ready for email.

5.     **Campaign management** – using the Mailjet API, a new campaign draft is created. The HTMLcontent is attached, a test email is sent, and upon approval the campaign isscheduled or immediately sent to the contact list[\[5\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#create-a-campaign-draft)[\[6\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#add-email-contents)[\[7\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#test-your-campaign)[\[8\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#send-the-campaign).

6.     **Next.js user interface** – a lightweight web application built with **Next.js** providescontrols to set topics, review content, approve edits, and start or schedulethe send. Next.js server actions or API routes call the backend services tofetch news, trigger the LLM summarisation pipeline and send emails. Indevelopment, Next.js’ MCP support (next‑devtools‑mcp) can be enabled to let anagent inspect the app’s state and logs[\[13\]](https://nextjs.org/docs/app/guides/mcp#:~:text=Enabling Next,Coding Agents).

7.     **Workflow orchestrator** – a job scheduler (e.g., Celery beat, Cron or serverless timers)triggers the pipeline at predefined intervals. For complex workflows, anorchestrator such as Airflow or LangChain’s AgentExecutor can coordinate tasks,including calls to MCP servers.

6 Implementationdetails
-----------------------

### 6.1 Technology stack

·        **Programming language** – Python is recommended because it has mature libraries for LLMintegration (openai, langchain), web development (FastAPI), template rendering (Jinja2, mjml wrapper), and Mailjet’s official SDK.

·        **LLM integration** – Use **OpenRouter** as the interface to large language models.OpenRouter supports tool‑calling across providers and allows you to routerequests to different models (GPT‑4, Claude, Gemini, etc.) while presenting aunified API[\[3\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=MCP servers are a popular,compatible tool calling)[\[4\]](https://openrouter.ai/docs/guides/features/tool-calling#:~:text=Tool calls ,to the user’s original question). You can convert MCP toolsto OpenAI‑compatible functions so the LLM can call firecrawl\_scrape or firecrawl\_search when it needs to fetch web content[\[3\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=MCP servers are a popular,compatible tool calling). Prompt templates shouldinclude few‑shot examples to ensure the LLM returns structured output[\[10\]](https://newsletter.theaiedge.io/p/deep-dive-how-to-automate-writing#:~:text=Selecting the top news).

·        **Content sources** – Start with [NewsAPI](https://newsapi.org/), which provides newsarticles filtered by query and date. The AI edge article shows how to call newsapi.get\_everything() with parameters such as q, from\_param and to[\[14\]](https://newsletter.theaiedge.io/p/deep-dive-how-to-automate-writing#:~:text=from newsapi import NewsApiClient). To supplement these,integrate the **Firecrawl MCP server**, which supports scraping single URLs,batch scraping, deep crawling and web searching[\[2\]](https://portkey.ai/docs/integrations/mcp-servers/firecrawl-mcp-server#:~:text=Key features). This allows the system toretrieve information from arbitrary websites beyond your normal RSS feeds.

·        **Image API** – Use the Unsplash API. Register an app and use the /search/photos endpoint to fetch images by keyword. The API is modern and easy tointegrate[\[11\]](https://unsplash.com/developers#:~:text=The most powerful photo engine,in the world).

·        **Template engine** – Use **MJML** for responsive email design. Predefine a templatewith placeholders for header, sections and footer. Use jinja2 to inject content.

·        **Mail sending** – Use Mailjet’s REST API via their Python SDK. Call create\_campaign\_draft(), add\_detail\_content(), test\_campaign() and send\_campaign() functions corresponding to the endpoints described earlier[\[5\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#create-a-campaign-draft)[\[6\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#add-email-contents)[\[7\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#test-your-campaign)[\[8\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#send-the-campaign).

o  **Web framework** – Use **FastAPI** for the backend that orchestrates LLM calls,Firecrawl scrapes and Mailjet integration. Build the frontend with **Next.js**,which offers server components, API routes and built‑in MCP support via the next‑devtools‑mcp package[\[9\]](https://nextjs.org/docs/app/guides/mcp#:~:text=Enabling Next,Coding Agents). For styling and UIcomponents, incorporate **Tailwind CSS** and **shadcn/ui**. Tailwindis a utility‑first CSS framework packed with classes like flex, pt‑4, text‑center and rotate‑90 that can be composed to build any design directly in your markup[\[15\]](https://tailwindcss.com/#:~:text=A utility,design, directly in your markup). Shadcn/ui is a collectionof accessible React components built with Radix UI primitives and styled withTailwind for Next.js applications, and you copy the actual TypeScript sourcecode into your project so you fully own and can customise the components[\[16\]](https://www.shadcn.io/ui#:~:text=Shadcn UI is a collection,You own the components completely). The Next.js app willdisplay a dashboard for configuration and preview, and call backend APIs totrigger the pipeline. This separation allows the heavy LLM work to run inPython while the UI leverages your existing Next.js skills and modern styling.

·        **Scheduling** – Use **Celery** with celery beat or Linux cron jobs to run the pipeline weekly. For serverlessdeployments, AWS EventBridge or Azure Functions Timer triggers can schedule thetasks.

o  **Database & Auth** – Use **Supabase** instead of a local SQLite or PostgreSQLinstance. Each Supabase project comes with a dedicated Postgres database plusauto‑generated REST APIs, built‑in authentication and user management, edgefunctions, a realtime API and file storage[\[17\]](https://supabase.com/docs/guides/platform#:~:text=Each project on Supabase comes,with). Supabase extends Postgreswith realtime functionality[\[18\]](https://supabase.com/docs/guides/database/overview#:~:text=Every Supabase project comes with,most stable and advanced databases) and integratesauthentication using JSON Web Tokens with row‑level security policies[\[19\]](https://supabase.com/docs/guides/auth#:~:text=Auth), allowing you to restrictaccess on a per‑user basis. You can store configuration, newsletter drafts andlogs securely in the Supabase database and use Supabase Auth to managedashboard users. Content may still be saved in Markdown/HTML files if desired.

### 6.2 Workflow steps

1.     **Configuration** – In the UI, choose topics and optionally input keywords for theupcoming newsletter. Store these preferences.

2.     **Fetch articles** – At the scheduled time, call NewsAPI (or other RSS feeds) to collectrecent articles for the topics. When you need content from specific websites orwhen NewsAPI doesn’t cover a source, call **Firecrawl’s firecrawl\_scrape or firecrawl\_search** tools via the MCPclient. These tools can scrape pages, perform search queries and returnstructured data[\[2\]](https://portkey.ai/docs/integrations/mcp-servers/firecrawl-mcp-server#:~:text=Key features). Handle API rate limits anddeduplicate results.

3.     **Select top news** – Use LangChain (or another agent framework) with prompts via **OpenRouter**to instruct the LLM to pick the most relevant stories from the list and returnstructured output[\[10\]](https://newsletter.theaiedge.io/p/deep-dive-how-to-automate-writing#:~:text=Selecting the top news). When the LLM needsadditional context not present in the article list, it can request firecrawl\_scrape or firecrawl\_search through OpenRouter’s tool‑calling interface[\[3\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=MCP servers are a popular,compatible tool calling).

4.     **Summarise content** – For each selected article:

5.     Extract the article text. If thearticle was obtained via NewsAPI or RSS, use a local scraper (newspaper3k/BeautifulSoup) to extract the body. If the article is from a site you accessed via **Firecrawl**,use Firecrawl’s structured output directly.

6.     Send the text to the LLM via **OpenRouter**,including a prompt that asks for a concise summary and commentary in thedesired tone. Provide your brand voice guidelines and allow the LLM to callFirecrawl again if additional context is needed. This leverages OpenRouter’stool‑calling capabilities to interleave LLM reasoning with external dataretrieval[\[3\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=MCP servers are a popular,compatible tool calling).

7.     **Generate images** – For each summary, call the Unsplash API with keywords extracted fromthe article (e.g., “artificial intelligence” or the main subject). Select thehighest‑quality image and save the URL. Alternatively call a Stable DiffusionAPI to generate an original image. Always attribute the photographer when usingUnsplash.

8.     **Assemble newsletter** – Render the MJML template with the generated content. Include aheader image, table of contents, separate sections for each article with title,summary, image and link, and a call‑to‑action or editorial note. Convert MJMLto HTML.

9.     **Create campaign draft** – Use Mailjet’s API to create a campaign draft. Provide the locale,sender name/email, subject line and contacts list ID[\[5\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#create-a-campaign-draft). Include a segment ID if thecampaign is targeted.

10\. **Add email content** – POST to /campaigndraft/{draft\_ID}/detailcontent with the HTML and text versions of the newsletter[\[6\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#add-email-contents).

11\. **Test** – POST to /campaigndraft/{draft\_ID}/test with a list of test recipients to preview the newsletter[\[7\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#test-your-campaign). The UI should display thetest email or forward it to you for review.

12\. **Approval and send** – Once approved in the UI,send the campaign via /campaigndraft/{draft\_ID}/send[\[8\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#send-the-campaign). Optionally allow schedulingby specifying a send time.

13\. **Logging and notifications** – Record each runand send status. Notify you on success or failure (e.g., via email or dashboardalert).

### 6.3 Prompt design andbrand voice

·        The Mailjet article warns thatChatGPT’s default voice is formal and may not match a brand’s tone[\[1\]](https://documentation.mailjet.com/hc/en-us/articles/35526276229531-Mailjet-s-AI-Assistant#:~:text=Why Use the AI Assistant?). Designprompts that include examples of your past newsletters to guide the model’sstyle (few‑shot prompting). Use parameters to control temperature and length.

·        Include guidelines on tone (e.g.,conversational, professional) and a call‑to‑action at the end. Use LangChain’sprompt templates so that the same structure can be reused weekly.

·        For languages other than English,test the translation capabilities of the LLM. Mailjet’s AI assistant supportsmultiple languages[\[1\]](https://documentation.mailjet.com/hc/en-us/articles/35526276229531-Mailjet-s-AI-Assistant#:~:text=Why Use the AI Assistant?); your modelshould provide similar translation quality.

7 Projectschedule
-----------------

Phase

Duration (approx.)

Key activities

Requirements & design

1 week

Meet with stakeholders to refine requirements, finalise topics, choose data sources and decide on image strategy. Design high‑level architecture and select technology stack.

Environment setup

1 week

Provision development environment, obtain API keys (NewsAPI, OpenAI, Unsplash, Mailjet), set up repository and CI/CD pipeline.

Content pipeline implementation

2 weeks

Implement data fetching, article selection (LangChain), summarisation prompts and image retrieval. Write unit tests and handle errors.

Template and Mailjet integration

1 week

Design MJML template, implement template rendering, integrate Mailjet API endpoints for draft creation, content upload, testing and sending.

Web interface development

1 week

Develop a minimal front‑end for topic configuration, previewing the generated newsletter and approving/scheduling sends. Integrate authentication if required.

Testing and refinement

1 week

End‑to‑end testing with your contact list, fix issues, refine prompts for tone and content quality, and optimise performance.

Deployment and training

1 week

Deploy the system to production (e.g., a cloud VM or container platform), schedule the weekly jobs and provide user training/documentation.

8 Risksand mitigation
---------------------

Risk

Mitigation

**LLM inaccuracies or hallucinations**

Use reliable data sources; cross‑check critical facts; require manual approval before sending; keep summaries concise.

**API limits or downtime**

Cache article responses; implement retries and back‑off; display errors in the UI; store a fallback newsletter from the previous week.

**Brand voice inconsistency**

Develop clear prompt templates with examples; review and adjust prompts regularly; include editing capabilities in the UI.

**Image licensing/compliance**

Use Unsplash under its API terms (include attribution). For generative models, ensure that outputs are appropriate.

**Privacy and compliance**

Use Mailjet to store and manage subscriber data; include unsubscribe links; avoid storing contact details locally; comply with GDPR/Spam laws.

**MCP complexity and session management**

Interacting with MCP servers is stateful and more complex than simple REST calls[\[12\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=Note that interacting with MCP,but is still somewhat complex). Use well‑tested client libraries (e.g., the Python mcp package) and encapsulate session handling in a service layer. Include retries and robust error handling to deal with rate limits and network issues[\[20\]](https://portkey.ai/docs/integrations/mcp-servers/firecrawl-mcp-server#:~:text=Key features).

**Scalability for future workflows**

Design the pipeline as modular services (data ingestion, summarisation, image retrieval, email assembly). New workflows can call existing modules or plug into the orchestrator.

9 Futureenhancements
--------------------

·        **Topic discovery** – automatically infer trending topics from social media or analyticsand suggest them for newsletters.

·        **Multi‑segment newsletters** – build different versions of the newsletter for different subscribersegments (e.g., beginners vs. advanced readers), using Mailjet’s segmentationfeatures.

·        **A/B testing** – integrate with Mailjet’s A/B testing APIs to test subject lines orlayouts.

·        **Analytics dashboard** – display open/click rates pulled from Mailjet’s statistics endpointand use this data to refine content.

·        **Multi‑channel distribution** – publish the newsletter as a blog post, LinkedIn article or socialpost simultaneously.

·        **Voice cloning or audio version** – generate audio summaries (text‑to‑speech) and embed them in theemail or host them externally.

10 Conclusion
-------------

Automating your newsletter creation will greatly reduce repetitivemanual work and allow you to focus on curating and commenting on content ratherthan assembling it. By combining curated data sources, LLM summarisation,simple image APIs and Mailjet’s campaign endpoints, you can build a reliablepipeline that produces a polished newsletter every week. The first iterationdescribed here lays the foundation for more advanced agent‑based workflows,such as generating custom reports or repurposing content across multipleplatforms.

[\[1\]](https://documentation.mailjet.com/hc/en-us/articles/35526276229531-Mailjet-s-AI-Assistant#:~:text=Why Use the AI Assistant?) Mailjet's AI Assistant – Mailjet Help Center

[https://documentation.mailjet.com/hc/en-us/articles/35526276229531-Mailjet-s-AI-Assistant](https://documentation.mailjet.com/hc/en-us/articles/35526276229531-Mailjet-s-AI-Assistant)

[\[2\]](https://portkey.ai/docs/integrations/mcp-servers/firecrawl-mcp-server#:~:text=Key features) [\[20\]](https://portkey.ai/docs/integrations/mcp-servers/firecrawl-mcp-server#:~:text=Key features) Firecrawl MCP server - Portkey Docs

[https://portkey.ai/docs/integrations/mcp-servers/firecrawl-mcp-server](https://portkey.ai/docs/integrations/mcp-servers/firecrawl-mcp-server)

[\[3\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=MCP servers are a popular,compatible tool calling) [\[12\]](https://openrouter.ai/docs/guides/guides/mcp-servers#:~:text=Note that interacting with MCP,but is still somewhat complex) Using MCP Servers with OpenRouter | OpenRouter | Documentation

[https://openrouter.ai/docs/guides/guides/mcp-servers](https://openrouter.ai/docs/guides/guides/mcp-servers)

[\[4\]](https://openrouter.ai/docs/guides/features/tool-calling#:~:text=Tool calls ,to the user’s original question) Tool & Function Calling | Use Tools with OpenRouter | OpenRouter |Documentation

[https://openrouter.ai/docs/guides/features/tool-calling](https://openrouter.ai/docs/guides/features/tool-calling)

[\[5\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#create-a-campaign-draft) Send campaigns using drafts

[https://dev.mailjet.com/email/guides/send-campaign-drafts/#create-a-campaign-draft](https://dev.mailjet.com/email/guides/send-campaign-drafts/#create-a-campaign-draft)

[\[6\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#add-email-contents) Send campaigns using drafts

[https://dev.mailjet.com/email/guides/send-campaign-drafts/#add-email-contents](https://dev.mailjet.com/email/guides/send-campaign-drafts/#add-email-contents)

[\[7\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#test-your-campaign) Send campaigns using drafts

[https://dev.mailjet.com/email/guides/send-campaign-drafts/#test-your-campaign](https://dev.mailjet.com/email/guides/send-campaign-drafts/#test-your-campaign)

[\[8\]](https://dev.mailjet.com/email/guides/send-campaign-drafts/#send-the-campaign) Send campaigns using drafts

[https://dev.mailjet.com/email/guides/send-campaign-drafts/#send-the-campaign](https://dev.mailjet.com/email/guides/send-campaign-drafts/#send-the-campaign)

[\[9\]](https://nextjs.org/docs/app/guides/mcp#:~:text=Enabling Next,Coding Agents) [\[13\]](https://nextjs.org/docs/app/guides/mcp#:~:text=Enabling Next,Coding Agents) Guides: Next.js MCP Server | Next.js

[https://nextjs.org/docs/app/guides/mcp](https://nextjs.org/docs/app/guides/mcp)

[\[10\]](https://newsletter.theaiedge.io/p/deep-dive-how-to-automate-writing#:~:text=Selecting the top news) [\[14\]](https://newsletter.theaiedge.io/p/deep-dive-how-to-automate-writing#:~:text=from newsapi import NewsApiClient) Deep Dive: How to Automate Writing Newsletters with LangChain, StableDiffusion and DiaChat

[https://newsletter.theaiedge.io/p/deep-dive-how-to-automate-writing](https://newsletter.theaiedge.io/p/deep-dive-how-to-automate-writing)

[\[11\]](https://unsplash.com/developers#:~:text=The most powerful photo engine,in the world)  Unsplash Image API | Free HDPhoto API

[https://unsplash.com/developers](https://unsplash.com/developers)

[\[15\]](https://tailwindcss.com/#:~:text=A utility,design, directly in your markup) Tailwind CSS - Rapidly build modern websites without ever leaving yourHTML.

[https://tailwindcss.com/](https://tailwindcss.com/)

[\[16\]](https://www.shadcn.io/ui#:~:text=Shadcn UI is a collection,You own the components completely) Shadcn UI React Components

[https://www.shadcn.io/ui](https://www.shadcn.io/ui)

[\[17\]](https://supabase.com/docs/guides/platform#:~:text=Each project on Supabase comes,with) Supabase Platform | Supabase Docs

[https://supabase.com/docs/guides/platform](https://supabase.com/docs/guides/platform)

[\[18\]](https://supabase.com/docs/guides/database/overview#:~:text=Every Supabase project comes with,most stable and advanced databases) Database | Supabase Docs

[https://supabase.com/docs/guides/database/overview](https://supabase.com/docs/guides/database/overview)

[\[19\]](https://supabase.com/docs/guides/auth#:~:text=Auth) Auth | Supabase Docs

[https://supabase.com/docs/guides/auth](https://supabase.com/docs/guides/auth)
