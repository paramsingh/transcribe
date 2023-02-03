import { useState } from "react";
import { Text, Box, Input, Button } from "@chakra-ui/react";
export const LoginForm = ({
  onClick,
}: {
  onClick: (email: string) => void;
}) => {
  const [email, setEmail] = useState<string>("");
  const [submitted, setSubmitted] = useState<boolean>(false);

  const onClickMethod = () => {
    setSubmitted(true);
    onClick(email);
  };

  return (
    <>
      <Text size="md" paddingBottom={10}>
        Enter your email address and we will send you a magic link to sign in.
        We will create your account if this is your first time signing in.
      </Text>
      <Box paddingBottom={10}>
        <Input
          size="lg"
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
        />
      </Box>
      <Box>
        <Button
          colorScheme="blue"
          onClick={onClickMethod}
          isLoading={submitted}
          loadingText={"Sending email"}
        >
          Continue
        </Button>
      </Box>
    </>
  );
};
