import { getMessaging, getToken } from "firebase/messaging";
import { app } from "./firebaseConfig"; // Your initialized Firebase app

const messaging = getMessaging(app);

export const requestAndSaveToken = async (userToken: string): Promise<string | undefined> => {
  try {
    const permission = await Notification.requestPermission();
    
    if (permission === 'granted') {
      const token = await getToken(messaging, { 
        vapidKey: 'BMDcMtP5aGTszEF_HMqdHwCFEhRdDVLssZmMlDpOrH5HRfQBdv8BQfzen4xz4mbEBOggR7qo8HjcXkGvjLRQtY0' 
      });

      if (token) {
        await fetch('http://localhost:8000/api/v1/students/me/fcm-token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${userToken}` 
          },
          body: JSON.stringify({ fcm_token: token })
        });
        return token;
      }
    }
  } catch (error) {
    console.error("FCM Error:", error);
  }
};
