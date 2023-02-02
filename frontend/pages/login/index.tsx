import { useState } from "react";
import { Box, Button, Heading, Input, Text } from "@chakra-ui/react";
import { sendEmail } from "../../client/login";
import { LoginForm } from "../../components/LoginForm";
import { LogoAndTitle } from "../../components/LogoAndTitle";
import { TranscriberHead } from "../../components/TranscriberHead";
enum CurrentView {
  LOGIN_FORM = "LOGIN_FORM",
  EMAIL_SENT = "EMAIL_SENT",
}

const Login = () => {
  const [currentView, setCurrentView] = useState<CurrentView>(
    CurrentView.LOGIN_FORM
  );
  const onClick = (email: string) => {
    console.log("hello");
    sendEmail(email)
      .then((data) => {
        if (data["success"]) {
          setCurrentView(CurrentView.EMAIL_SENT);
        }
      })
      .catch((err) => {
        console.log(err);
      });
  };
  return (
    <>
      <TranscriberHead title="Transcriber | Login" />
      <main>
        <div>
          <LogoAndTitle />
          <Heading as="h2" size="xl" paddingBottom={10}>
            Sign in to transcriber
          </Heading>
          {currentView == CurrentView.LOGIN_FORM && (
            <LoginForm onClick={onClick} />
          )}
          {currentView == CurrentView.EMAIL_SENT && (
            <Text size="md" paddingBottom={10}>
              We have sent you an email with a magic link to sign in. Please
              check your inbox.
            </Text>
          )}
        </div>
      </main>
    </>
  );
};

export default Login;
