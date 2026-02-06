# SMU Digital Library Frontend

Modern Vue 3 frontend application for SMU Digital Library.

## 🚀 Tech Stack

- **Vue 3** - Progressive JavaScript Framework
- **Vite** - Next Generation Frontend Tooling
- **Pinia** - State Management
- **Vue Router** - Official Router
- **Axios** - HTTP Client
- **Vue I18n** - Internationalization
- **TailwindCSS** - Utility-first CSS Framework
- **VueUse** - Collection of Essential Vue Composition Utilities

## 📦 Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🌐 Available at

- Development: http://localhost:3000
- Backend API: http://localhost:8000

## 📁 Project Structure

```
src/
├── assets/          # Static assets
├── components/      # Reusable components
│   ├── common/      # Common UI components
│   ├── content/     # Content-specific components
│   └── layout/      # Layout components
├── composables/     # Composition API hooks
├── locales/         # i18n translations
├── router/          # Vue Router configuration
├── services/        # API services
├── stores/          # Pinia stores
├── utils/           # Utility functions
├── views/           # Page components
├── App.vue          # Root component
└── main.js          # Application entry point
```

## 🔑 Environment Variables

Create `.env.local` file:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1
```

## 🌍 Supported Languages

- Turkmen (tm) - Default
- Russian (ru)
- English (en)

## 📝 Features

- ✅ Full-text search integration
- ✅ Article, Book, Dissertation browsing
- ✅ User authentication (JWT)
- ✅ Bookmarks & Ratings
- ✅ Multi-language support
- ✅ Responsive design
- ✅ Category filtering
- ✅ Advanced search
