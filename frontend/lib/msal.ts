import { PublicClientApplication, type Configuration } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_MICROSOFT_CLIENT_ID ?? "",
    authority: "https://login.microsoftonline.com/organizations",
    redirectUri: process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost"
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: true
  }
};

export const msalInstance = new PublicClientApplication(msalConfig);

