import { InfoIcon } from "@chakra-ui/icons";
import {
  Popover,
  PopoverTrigger,
  IconButton,
  Portal,
  PopoverContent,
  PopoverArrow,
  PopoverCloseButton,
  PopoverHeader,
  PopoverBody,
} from "@chakra-ui/react";
import Link from "next/link";

export const PopoverInfo = ({
  transcriptionID,
}: {
  transcriptionID: string;
}) => {
  return (
    <Popover>
      <PopoverTrigger>
        <IconButton
          icon={<InfoIcon />}
          aria-label="info"
          marginLeft={2}
          marginRight={2}
          marginBottom={5}
        />
      </PopoverTrigger>
      <Portal>
        <PopoverContent>
          <PopoverArrow />
          <PopoverCloseButton />
          <PopoverHeader>Note</PopoverHeader>
          <PopoverBody>
            We will redirect you to the transcription when it is ready, it may
            take some time. If you do not want to wait, come back to{" "}
            <Link href={`/result/${transcriptionID}`}>this link</Link> later and
            we should have it ready.
          </PopoverBody>
        </PopoverContent>
      </Portal>
    </Popover>
  );
};
