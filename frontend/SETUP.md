# SMU Frontend - Setup Instructions

## 📋 Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will be available at **http://localhost:3000**

### 3. Build for Production

```bash
npm run build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable Vue components
│   │   ├── common/      # UI components (cards, buttons, etc.)
│   │   └── layout/      # Layout components (header, footer, sidebar)
│   ├── views/           # Page components (routes)
│   ├── stores/          # Pinia state management
│   ├── services/        # API service layer
│   ├── router/          # Vue Router configuration
│   ├── locales/         # i18n translations (tm, ru, en)
│   ├── App.vue          # Root component
│   ├── main.js          # Application entry point
│   └── style.css        # Global styles with Tailwind
├── public/              # Static assets
├── index.html           # HTML template
├── package.json         # Dependencies
├── vite.config.js       # Vite configuration
└── tailwind.config.js   # Tailwind CSS configuration
```

## 🔑 Key Features Implemented

✅ **Complete UI/UX**

- Responsive design with TailwindCSS
- Header with search and language switcher
- Category sidebar for filtering
- Content cards with images, ratings, views
- Pagination component

✅ **Pages**

- Home page with featured content
- Article list with filters (local/foreign)
- Article detail with rating and bookmarks
- Books, Dissertations (same structure)
- Search page
- Login/Register
- Profile and Bookmarks
- 404 Not Found

✅ **State Management (Pinia)**

- Auth store (login, register, logout)
- Content store (articles, books, dissertations)
- Bookmarks store
- Search store

✅ **API Integration**

- Axios client with interceptors
- JWT token management with auto-refresh
- Services for all API endpoints
- Error handling

✅ **Internationalization (i18n)**

- Turkmen (default)
- Russian
- English
- Language switcher in header

✅ **Features**

- Authentication with JWT
- Bookmarking content
- Rating system
- View tracking
- Category filtering
- Full-text search
- Responsive design

## 🌐 API Configuration

The frontend is configured to proxy API requests to the backend:

- **Development**: http://localhost:8000
- **Production**: Configure in `.env.production`

## 🎨 Customization

### Colors

Edit [tailwind.config.js](tailwind.config.js#L9-L19) to change primary colors:

```js
colors: {
  primary: {
    500: '#0ea5e9',
    600: '#0284c7',
    700: '#0369a1',
  }
}
```

### Translations

Add or edit translations in `src/locales/`:

- `tm.json` - Turkmen
- `ru.json` - Russian
- `en.json` - English

## 🔧 Development Tips

1. **Backend must be running** for API calls to work
2. Use **Vue DevTools** browser extension for debugging
3. **Hot reload** is enabled by default
4. Check browser console for errors

## 📦 Dependencies

- **Vue 3** - Progressive JavaScript framework
- **Vite** - Fast build tool
- **Pinia** - State management
- **Vue Router** - Routing
- **Axios** - HTTP client
- **Vue I18n** - Internationalization
- **TailwindCSS** - Utility-first CSS
- **VueUse** - Composition utilities

## 🐛 Troubleshooting

### API not connecting

- Ensure backend is running on port 8000
- Check CORS settings in Django backend
- Verify proxy configuration in `vite.config.js`

### Build errors

```bash
rm -rf node_modules
npm install
```

### Port already in use

Edit `vite.config.js` and change the port:

```js
server: {
  port: 3001; // Change to any available port
}
```

## 📱 Mobile Support

The application is fully responsive and works on:

- Desktop (1280px+)
- Tablet (768px - 1279px)
- Mobile (320px - 767px)

## 🚢 Production Deployment

1. Build the application:

```bash
npm run build
```

2. The `dist/` folder contains the production build

3. Deploy to:

- Static hosting (Netlify, Vercel)
- Nginx/Apache server
- Docker container

4. Configure environment variables for production API URL

## 📝 Next Steps

To extend the application:

1. Add more filters (date range, author, etc.)
2. Implement advanced search with facets
3. Add user profile editing
4. Implement social features (comments, sharing)
5. Add PDF viewer for documents
6. Implement admin dashboard
7. Add analytics and reporting

## 💡 Support

For issues or questions:

- Check browser console for errors
- Verify backend API is accessible
- Review network tab in DevTools
- Check this documentation
