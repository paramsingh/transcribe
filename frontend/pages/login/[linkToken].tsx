import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { redeemToken } from "../../client/login";
import { LogoAndTitle } from "../../components/LogoAndTitle";
import { TranscriberHead } from "../../components/TranscriberHead";
import { setSessionToken } from "../../utils/sessionTokenUtils";

export default function RedeemToken() {
  const router = useRouter();
  const token = router.query.linkToken as string;

  useEffect(() => {
    if (token) {
      redeemToken(token)
        .then((data) => {
          const sessionToken = data.session;
          if (!sessionToken) {
            alert("login failed");
          }
          // put session token in local storage
          setSessionToken(sessionToken);
          setTimeout(() => {
            router.push("/");
          }, 1000);
        })
        .catch((err) => {
          alert("login failed");
        });
    }
  });

  return (
    <>
      <TranscriberHead
        title={`Redeem token`}
        description="redeem login token for transcribe.param.codes"
      />
      <main>
        <LogoAndTitle />
        <div>
          <h1>Signing you in...</h1>
        </div>
      </main>
    </>
  );
}
