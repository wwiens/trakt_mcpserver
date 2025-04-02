# 🎬 MCP Trakt: Your AI's Gateway to Entertainment Data

![MCP Trakt](https://img.shields.io/badge/MCP-Trakt-ff69b4)
![Built with Cursor](https://img.shields.io/badge/Built%20with-Cursor-blue)
![Powered by Claude](https://img.shields.io/badge/Powered%20by-Claude%203.7%20Sonnet-blueviolet)

A Model Context Protocol (MCP) server that creates a bridge between AI language models and the Trakt.tv API, allowing LLMs to access real-time entertainment data.

## 🤖 What is MCP?

Model Context Protocol (MCP) is an open specification that enables Large Language Models (LLMs) like Claude to interact with external systems and data sources. 

MCP creates a standardized way for AI models to:

- Access real-time data beyond their training cutoff date
- Connect to external APIs and web services through dedicated servers
- Execute specialized tools and functions securely
- Read from and write to external resources
- Process complex data that would be difficult to handle in text-only formats

At its core, MCP works by defining:

1. **Resources**: Structured data sources that an AI can read from or write to (like `trakt://shows/trending`)
2. **Tools**: Functions that the AI can invoke to perform specific actions (like `fetch_trending_shows`)
3. **Sessions**: Secure connections between the AI and MCP servers

MCP servers like this one act as bridges between AI models and the external world, allowing them to be extended with new capabilities without requiring retraining.

## 📺 What is Trakt?

[Trakt.tv](https://trakt.tv) is a platform that automatically tracks what TV shows and movies you watch. The service offers:

- Comprehensive tracking of viewing habits across multiple streaming services
- Social features to share and discuss what you're watching with friends
- Personalized recommendations based on your viewing history
- Extensive APIs that developers can use to build applications

Trakt has become the standard for entertainment tracking with:
- Over 14 million users tracking their viewing habits
- Data on millions of movies and TV shows, including detailed metadata
- Integration with popular media players and streaming services

This MCP server taps into Trakt's rich API ecosystem to bring real-time entertainment data directly to your conversations with AI assistants like Claude.

## 🚀 The Cursor Development Experience

This entire project was developed using [Cursor](https://cursor.sh/), a code editor built for the AI era, with Claude 3.7 Sonnet generating all code. This approach demonstrates:

- How AI-assisted development can dramatically accelerate building specialized MCP servers
- The capabilities of modern AI in writing functional, well-structured code
- A collaborative workflow between human intent and AI implementation

## ✨ Features

- Exposes Trakt API data through MCP resources
- Provides tools for fetching real-time movies and shows information
- Enables AI models to offer personalized entertainment recommendations
- Updates regularly with the latest data from Trakt.tv

### 📺 Currently Trending Shows

As of April 2025, you can access trending shows like:
- "The White Lotus" (2021) - 7,870 watchers
- "Daredevil: Born Again" (2025) - 6,738 watchers
- "Severance" (2022) - 4,507 watchers

### 🎥 Currently Trending Movies

The hottest movies right now:
- "Black Bag" (2025) - 1,491 watchers
- "A Working Man" (2025) - 1,226 watchers
- "Mickey 17" (2025) - 764 watchers

## 🔌 Available Resources

### Show Resources
| Resource | Description | Example Data |
|----------|-------------|--------------|
| `trakt://shows/trending` | Most watched shows over the last 24 hours | Show title, year, watchers count |
| `trakt://shows/popular` | Most popular shows based on ratings | Show title, year, popular score |
| `trakt://shows/favorited` | Most favorited shows | Show title, year, favorites count |
| `trakt://shows/played` | Most played shows | Show title, year, play count |
| `trakt://shows/watched` | Most watched shows by unique users | Show title, year, watcher count |

### Movie Resources
| Resource | Description | Example Data |
|----------|-------------|--------------|
| `trakt://movies/trending` | Most watched movies over the last 24 hours | Movie title, year, watchers count |
| `trakt://movies/popular` | Most popular movies based on ratings | Movie title, year, popular score |
| `trakt://movies/favorited` | Most favorited movies | Movie title, year, favorites count |
| `trakt://movies/played` | Most played movies | Movie title, year, play count |
| `trakt://movies/watched` | Most watched movies by unique users | Movie title, year, watcher count |

## 🛠️ Available Tools

### Show Tools
```python
# Get trending shows with optional limit parameter
fetch_trending_shows(limit=10)

# Get popular shows with optional limit parameter
fetch_popular_shows(limit=10)

# Get favorited shows with optional limit and period parameters
fetch_favorited_shows(limit=10, period="weekly")

# Get most played shows with optional limit and period parameters
fetch_played_shows(limit=10, period="weekly")

# Get most watched shows with optional limit and period parameters
fetch_watched_shows(limit=10, period="weekly")
```

### Movie Tools
```python
# Get trending movies with optional limit parameter
fetch_trending_movies(limit=10)

# Get popular movies with optional limit parameter
fetch_popular_movies(limit=10)

# Get favorited movies with optional limit and period parameters
fetch_favorited_movies(limit=10, period="weekly")

# Get most played movies with optional limit and period parameters
fetch_played_movies(limit=10, period="weekly")

# Get most watched movies with optional limit and period parameters
fetch_watched_movies(limit=10, period="weekly")
```

## 🚀 Setup

1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/mcp-trakt.git
   cd mcp-trakt
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` to add your Trakt API credentials:
   ```
   TRAKT_CLIENT_ID=your_client_id
   TRAKT_CLIENT_SECRET=your_client_secret
   ```

4. **Run the server**
   ```bash
   python server.py
   ```

## 🧪 Development & Testing

### Testing with MCP Inspector
```bash
mcp dev server.py
```

### Installing in Claude Desktop
```bash
mcp install server.py
```

## 📝 Using with Claude

Once installed, you can ask Claude questions like:

- "What shows are trending right now?"
- "Can you recommend some popular movies this week?"
- "What are the most watched shows of the month?"

Claude will use this MCP server to provide you with real-time data from Trakt.

## 🔮 Future Development

- Adding user authentication to access personal watch history
- Implementing show and movie search capabilities
- Adding calendar events for upcoming episodes
- Supporting scrobbling (tracking what you're watching)
- Implementing recommendations based on watch history

## 
## 📄 License

[MIT License](LICENSE)

---

<div align="center">
  <p>Built with 🧠 AI and human collaboration</p>
  <p>Powered by Cursor + Claude 3.7 Sonnet</p>
</div>