# 💾 Product Requirements Document

### **Project:** Hands-Free Cooking App (MVP)

### **Milestone 1:** Core Recipe Interaction via Voice

### **Date:** 2025-08-13

---

## ✅ **Overview**

This milestone delivers a **progressive web app** optimized for **mobile and tablet**. Users will log in via Google, paste a recipe link, and enter “cook mode.” The app will extract the recipe, persist it server-side, and open a live voice-driven assistant session via WebSocket. The assistant helps manage steps, ingredients, and substitutions in real-time.

---

## 🔑 **Goals**

* Mobile-first UX with intuitive flow
* Real-time voice-driven interaction with recipes
* Server-assisted recipe parsing and persistence
* Real-time agent session via WebSocket

---

## 🧑‍💻 **Tech Stack**

| Concern           | Stack                           |
| ----------------- | ------------------------------- |
| UI Framework      | Whatevers easiest (react/vue/svelte) |
| Styling           | Tailwind CSS                    |
| Auth              | Google OAUTH (Google provider) |
| Voice Recognition | Web Speech API (browser-native) |
| WebSocket Client  | Native `WebSocket` in JS        |
| Web App Type      | Progressive Web App (PWA)       |
| Backend           | Node (Go or Python)             |
| DBs               | Vector DB + NoSQL (MongoDB)     |

---

## 📱 **User Flow**

1. **Landing Page**

   * User sees app name, brief description, and **“Sign in with Google”** button.

2. **Authentication**

   * User signs in via Google using oAuth consent screen.

3. **Recipe Entry**

   * User pastes a recipe URL into a form input.
   * On submit: client sends the URL to backend via REST.

4. **Cook Mode**

   * After response, the UI transitions to "cook mode":

     * Client requests **microphone access**
     * Client opens **WebSocket** to backend with `recipeId` in the connection payload.

5. **Live Agent Interaction**

   * AI agent runs on backend with full recipe context.
   * User speaks commands like:

     * “What’s the next step?”
     * “How much salt again?”
     * “What can I use instead of heavy cream?”
   * Backend parses these, responds via WebSocket (TTS optional).

---

## 🧪 **Success Criteria**

* ✅ User can log in and paste recipe URL
* ✅ Recipe is parsed and stored in DB
* ✅ User enters “cook mode” with mic access
* ✅ WebSocket session opens with `recipeId`
* ✅ AI agent responds to voice queries about recipe steps, ingredients, and substitutions
