import { Heading } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { getRecentTranscriptions } from "../client/api-client";
import { TranscriptionTable } from "./TranscriptionTable";

export const RecentTranscriptions = () => {
  const [transcriptions, setTranscriptions] = useState<any>(null);
  useEffect(() => {
    getRecentTranscriptions()
      .then((data) => {
        setTranscriptions(data.transcriptions);
      })
      .catch((err) => {
        console.error(err);
      });
  }, []);
  if (!transcriptions) return null;
  return (
    <>
      <Heading size="xl" paddingBottom={5}>
        Recent Transcriptions
      </Heading>
      <TranscriptionTable transcriptions={transcriptions} showOnlySuccessful />
    </>
  );
};
