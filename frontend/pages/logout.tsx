import { useEffect, useState } from "react";
import { Text } from "@chakra-ui/react";
import { TranscriberHead } from "../components/TranscriberHead";
import { logOut } from "../client/login";
import {
  getSessionToken,
  removeSessionToken,
} from "../utils/sessionTokenUtils";
import { LogoAndTitle } from "../components/LogoAndTitle";

export default function Logout() {
  const [loggedOut, setLoggedOut] = useState<boolean>(false);
  useEffect(() => {
    if (!loggedOut) {
      const sessionToken = getSessionToken();
      if (!sessionToken) {
        alert("not logged in");
      }
      logOut(sessionToken as string)
        .then((data) => {
          removeSessionToken();
          setLoggedOut(true);
        })
        .catch((err) => {
          console.error(err);
        });
    }
  }, [loggedOut]);
  return (
    <>
      <TranscriberHead
        title={`Transcriber | Logout`}
        description="Sign out from transcribe.param.codes"
      />
      <main>
        <LogoAndTitle />
        {loggedOut ? (
          <Text size="md" paddingBottom={10}>
            You have been logged out.
          </Text>
        ) : (
          <Text size="md" paddingBottom={10}>
            Logging you out...
          </Text>
        )}
      </main>
    </>
  );
}
