import apiService from './apiService'

export interface ScreenShareSession {
  sessionId: string
  url: string
  status: string
}

export const screenShareService = {
  async createSession(): Promise<ScreenShareSession> {
    try {
      return await apiService.createScreenShareSession()
    } catch (error) {
      console.error('Screen share error:', error)
      throw new Error('Failed to create screen sharing session')
    }
  },

  loadJitsi(containerId: string, roomName: string, options = {}) {
    // Load Jitsi Meet External API
    const script = document.createElement('script')
    script.src = 'https://meet.jit.si/external_api.js'
    script.async = true
    script.onload = () => {
      this.initializeJitsi(containerId, roomName, options)
    }
    document.head.appendChild(script)
  },

  initializeJitsi(containerId: string, roomName: string, options: any = {}) {
    // @ts-ignore - Jitsi Meet API
    if (typeof JitsiMeetExternalAPI !== 'undefined') {
      const domain = 'meet.jit.si'
      // @ts-ignore
      const api = new JitsiMeetExternalAPI(domain, {
        roomName: roomName,
        width: '100%',
        height: '100%',
        parentNode: document.getElementById(containerId),
        userInfo: {
          displayName: 'Math Solver User'
        },
        configOverwrite: {
          startWithAudioMuted: true,
          startWithVideoMuted: true,
          prejoinPageEnabled: false
        },
        interfaceConfigOverwrite: {
          DEFAULT_BACKGROUND: '#111',
          DEFAULT_LOCAL_DISPLAY_NAME: 'You',
          SHOW_JITSI_WATERMARK: false,
          SHOW_WATERMARK_FOR_GUESTS: false,
          DEFAULT_REMOTE_DISPLAY_NAME: 'Participant',
          TOOLBAR_BUTTONS: [
            'microphone', 'camera', 'closedcaptions', 'desktop', 
            'fullscreen', 'fodeviceselection', 'hangup', 'profile',
            'chat', 'recording', 'livestreaming', 'etherpad', 'sharedvideo',
            'settings', 'raisehand', 'videoquality', 'filmstrip', 'invite',
            'feedback', 'stats', 'shortcuts', 'tileview', 'videobackgroundblur',
            'download', 'help', 'mute-everyone', 'security'
          ]
        },
        ...options
      })

      return api
    }
  },

  generateRoomName(): string {
    const timestamp = Date.now()
    const random = Math.random().toString(36).substring(2, 8)
    return `math-solver-${timestamp}-${random}`
  }
}

export default screenShareService