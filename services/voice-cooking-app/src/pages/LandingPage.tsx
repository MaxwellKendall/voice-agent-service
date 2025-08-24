import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'

const LandingPage: React.FC = () => {
  const { signInWithGoogle } = useAuth()
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  const handleSignIn = async () => {
    try {
      await signInWithGoogle()
    } catch (error) {
      console.error('Sign in error:', error)
    }
  }

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index)
  }

  const faqData = [
    {
      question: "How does the voice cooking assistant work?",
      answer: "Simply paste any recipe URL, click 'Start Voice Cooking', and our AI assistant will guide you through every step with voice instructions. You can ask questions, request clarification, and get real-time help while keeping your hands free for cooking."
    },
    {
      question: "What recipe sources do you support?",
      answer: "We support recipes from TikTok, Pinterest, Instagram, YouTube, and virtually any website on the internet. Just paste the URL and our AI will extract all the ingredients, instructions, and cooking times automatically."
    },
    {
      question: "Is it really free to use?",
      answer: "Yes! Voice Cooking is completely free to use. You can import unlimited recipes and use the voice assistant as much as you want. No hidden fees, no subscription required."
    },
    {
      question: "Do I need to install anything?",
      answer: "No installation required! Voice Cooking works entirely in your web browser. Just grant microphone access when prompted and you're ready to start cooking with voice guidance."
    },
    {
      question: "Can I use it on my phone?",
      answer: "Yes! Voice Cooking works on both desktop and mobile devices. The voice assistant is optimized for hands-free cooking, making it perfect for use on your phone in the kitchen."
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">

      {/* Hero Section */}
      <div className="max-w-4xl mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
          Cook what <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">speaks</span> to you
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Hands free cooking
        </p>
        
        <button
          onClick={handleSignIn}
          className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 text-lg"
        >
          Try now FREE
        </button>
      </div>

      {/* Import Section */}
      <div className="py-16 bg-white/50 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Import recipes <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">free </span>
            from anywhere
          </h3>
          
          <div className="flex justify-center items-center space-x-8 mb-8">
            {/* TikTok */}
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-white rounded-xl flex items-center justify-center mb-2">
                <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
                </svg>
              </div>
              <span className="text-sm font-medium text-gray-700">TikTok</span>
            </div>

            {/* Pinterest */}
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-white rounded-xl flex items-center justify-center mb-2">
                <svg className="w-8 h-8 text-red-600" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.174-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.357-.629-2.746-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24.009 12.017 24.009c6.624 0 11.99-5.367 11.99-11.988C24.007 5.367 18.641.001 12.017.001z"/>
                </svg>
              </div>
              <span className="text-sm font-medium text-gray-700">Pinterest</span>
            </div>

            {/* Chrome/Web */}
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-white rounded-xl flex items-center justify-center mb-2">
                <svg width="29" height="29" viewBox="0 0 29 29" fill="none" xmlns="http://www.w3.org/2000/svg"><g clip-path="url(#clip0_15989_21032)"><path d="M14.1656 0.0039723C14.1656 0.0039723 22.515 -0.369111 26.9415 7.9864H13.4551C13.4551 7.9864 10.9101 7.90478 8.73588 10.9788C8.11133 12.2691 7.43994 13.5982 8.1933 16.2175C7.10815 14.3871 2.43184 6.28032 2.43184 6.28032C2.43184 6.28032 5.73024 0.334306 14.1656 0.0039723Z" fill="#EF3F36"></path><path d="M26.5082 21.2152C26.5082 21.2152 22.6555 28.603 13.178 28.2377C14.349 26.2207 19.9231 16.6099 19.9231 16.6099C19.9231 16.6099 21.2698 14.4569 19.6811 11.0448C18.8731 9.85947 18.0495 8.61974 15.3951 7.95908C17.5303 7.93964 26.9181 7.95908 26.9181 7.95908C26.9181 7.95908 30.4351 13.7768 26.5082 21.2152Z" fill="#FCD900"></path><path d="M1.88146 21.2735C1.88146 21.2735 -2.6192 14.2588 2.43965 6.26855C3.60677 8.28554 9.18087 17.8963 9.18087 17.8963C9.18087 17.8963 10.3831 20.1348 14.1421 20.469C15.5747 20.3641 17.0658 20.2747 18.9707 18.3199C17.9207 20.1698 13.2092 28.2533 13.2092 28.2533C13.2092 28.2533 6.38602 28.3776 1.88146 21.2735Z" fill="#61BC5B"></path><path d="M13.1741 28.3078L15.0712 20.4264C15.0712 20.4264 17.1556 20.2631 18.9043 18.355C17.8192 20.2554 13.1741 28.3078 13.1741 28.3078Z" fill="#5AB055"></path><path d="M7.81077 14.2433C7.81077 10.769 10.6408 7.95142 14.1304 7.95142C17.6201 7.95142 20.4501 10.769 20.4501 14.2433C20.4501 17.7176 17.6201 20.5352 14.1304 20.5352C10.6408 20.5313 7.81077 17.7176 7.81077 14.2433Z" fill="white"></path><path d="M8.8686 14.2433C8.8686 11.352 11.2224 9.00464 14.1304 9.00464C17.0346 9.00464 19.3923 11.3481 19.3923 14.2433C19.3923 17.1347 17.0385 19.4821 14.1304 19.4821C11.2263 19.4821 8.8686 17.1347 8.8686 14.2433Z" fill="url(#paint0_linear_15989_21032)"></path><path d="M26.9142 7.96319L19.1034 10.2444C19.1034 10.2444 17.9246 8.52281 15.3912 7.96319C17.5889 7.95153 26.9142 7.96319 26.9142 7.96319Z" fill="#EACA05"></path><path d="M8.04107 15.9299C6.94421 14.0373 2.43184 6.28027 2.43184 6.28027L8.21673 11.9776C8.21673 11.9776 7.6234 13.194 7.8459 14.935L8.04107 15.9299Z" fill="#DF3A32"></path></g><defs><linearGradient id="paint0_linear_15989_21032" x1="14.1302" y1="9.07859" x2="14.1302" y2="19.1667" gradientUnits="userSpaceOnUse"><stop stop-color="#86BBE5"></stop><stop offset="1" stop-color="#1072BA"></stop></linearGradient><clipPath id="clip0_15989_21032"><rect width="28.378" height="28.3636" fill="white"></rect></clipPath></defs></svg>
              </div>
              <span className="text-sm font-medium text-gray-700">Any Website</span>
            </div>
          </div>

          <p className="text-gray-600">
            Paste the URL and get started
          </p>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="py-16 bg-white/50 backdrop-blur-sm">
        <div className="max-w-3xl mx-auto px-6">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-12">
            Frequently Asked Questions
          </h3>
          
          <div className="space-y-4">
            {faqData.map((faq, index) => (
              <div key={index} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <button
                  onClick={() => toggleFaq(index)}
                  className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <span className="font-medium text-gray-900">{faq.question}</span>
                  <svg
                    className={`w-5 h-5 text-gray-500 transition-transform ${
                      openFaq === index ? 'rotate-45' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </button>
                
                {openFaq === index && (
                  <div className="px-6 pb-4">
                    <p className="text-gray-600 leading-relaxed">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default LandingPage
