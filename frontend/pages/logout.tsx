import { useEffect, useState } from "react";
import { Text } from "@chakra-ui/react";
import { TranscriberHead } from "../components/TranscriberHead";
import { logOut } from "../client/login";

export default function Logout() {
  const [loggedOut, setLoggedOut] = useState<boolean>(false);
  useEffect(() => {
    if (!loggedOut) {
      const sessionToken = localStorage.getItem("sessionToken");
      if (!sessionToken) {
        alert("not logged in");
      }
      logOut(sessionToken as string)
        .then((data) => {
          localStorage.removeItem("sessionToken");
          setLoggedOut(true);
        })
        .catch((err) => {
          console.error(err);
        });
    }
  }, []);
  return (
    <>
      <TranscriberHead title={`Transcriber | Logout`} />
      <main>
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
