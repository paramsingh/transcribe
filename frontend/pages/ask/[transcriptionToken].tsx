import { Box, Button, Divider, Heading, Input, Text } from "@chakra-ui/react";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { getAnswer, getDetailsForToken } from "../../client/api-client";
import { LogoAndTitle } from "../../components/LogoAndTitle";
import { TranscriberHead } from "../../components/TranscriberHead";
import { YoutubeEmbed } from "../../components/YoutubeEmbed";

export default function TranscriptionAsk() {
  const router = useRouter();
  const transcriptionToken = router.query.transcriptionToken as string;
  const [question, setQuestion] = useState<string>("");
  const [answer, setAnswer] = useState<string>("");
  const [waiting, setWaiting] = useState<boolean>(false);
  const [link, setLink] = useState<string>("");
  const [hasEmbeddings, setHasEmbeddings] = useState<boolean>(true);

  useEffect(() => {
    if (!transcriptionToken) return;
    getDetailsForToken(transcriptionToken).then((data) => {
      setLink(data.link);
      setHasEmbeddings(data.has_embeddings);
    });
  });

  const submit = () => {
    setWaiting(true);
    getAnswer(transcriptionToken, question).then((data) => {
      setAnswer(data.answer);
      setWaiting(false);
    });
  };

  return (
    <>
      <TranscriberHead
        title={"Ask"}
        description={`Ask questions about the Youtube video: ${link}`}
      />
      <main>
        <LogoAndTitle />
        {link && (
          <>
            <YoutubeEmbed link={link} />
            <Divider />
          </>
        )}
        <Heading as="h2" size="2xl" marginTop={5} marginBottom={5}>
          Ask a question
        </Heading>
        <Input
          size="lg"
          placeholder="Enter your question"
          marginBottom={5}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={waiting}
        />
        <Button
          colorScheme={"blue"}
          onClick={submit}
          isLoading={waiting}
          loadingText={"Getting an answer"}
        >
          Ask
        </Button>
        {answer !== "" && (
          <Box marginTop={5}>
            <Heading size="lg" marginBottom={5}>
              Answer
            </Heading>
            <Text>{answer}</Text>
          </Box>
        )}
      </main>
    </>
  );
}
