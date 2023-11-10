import "../styles/App.css";
import React, { useEffect, useState } from "react";
import { QuestionCircleOutlined } from "@ant-design/icons";
import { FloatButton, QRCode, Button } from "antd";
import { useGoogleLogin } from "@react-oauth/google";

export function Login() {
  const [Blogin, setBlogin] = useState(false);
  const [Ylogin, setYlogin] = useState(false);

  const [Bsignined, setBsignined] = useState(
    sessionStorage.getItem("SESSDATA") !== null
  );
  const [Ysignined, setYsignined] = useState(
    sessionStorage.getItem("access_token") !== null
  );

  const [Bprompt, setBprompt] = useState("Scan the QR code on the mobile app");
  const [QR, setQR] = useState("https://bilibili.com");

  const [poll, setPoll] = useState(0);

  useEffect(() => {
    if (Blogin && !Bsignined) {
      fetch("http://localhost:8000/bilibili/qrcode", {
        method: "get",
        credentials: "include",
      }).then(async (res) => {
        let data = await res.json();
        data = data.data;
        let url = data.url;
        let key = data.qrcode_key;
        setQR(url);
        console.log(url);
        setPoll(
          setInterval(() => {
            if (!Bsignined) {
              fetch(
                `http://localhost:8000/bilibili/qrcode/poll?qrcode_key=${key}`,
                {
                  method: "get",
                  credentials: "include",
                }
              ).then(async (response) => {
                let data = await response.json();
                data = data.data;
                if (data.code === 0) {
                  setBsignined(true);
                  sessionStorage.setItem("SESSDATA", data.SESSDATA);
                  return;
                }
              });
            }
          }, 1000)
        );
      });
    }
  }, [Blogin, Bsignined]);

  useEffect(() => {
    if (!Blogin || Bsignined) clearInterval(poll);
  }, [Bsignined, Blogin]);

  const bilibiliLogout = () => {
    setBsignined(false);
    setBprompt("Scan the QR code on the mobile app");
    sessionStorage.removeItem("SESSDATA");
  };

  const googleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      sessionStorage.setItem("access_token", tokenResponse.access_token);
      setYsignined(true);
    },
    onError: (errorMsg) => {
      alert("Youtube Login Error: " + errorMsg);
    },
    scope:
      "https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/userinfo.profile",
  });

  const googleLogout = () => {
    setYsignined(false);
    sessionStorage.removeItem("access_token");
  };

  return (
    <div className="App">
      <h1>B2Y</h1>
      <div className="login-container">
        <div
          className="app-login"
          onMouseEnter={() => setBlogin(true)}
          onMouseLeave={() => setBlogin(false)}
        >
          <img
            src="images/bilibili.png"
            alt="Bilibili"
            className="logoimg"
            style={{ display: Blogin ? "none" : "block" }}
          />
          <div style={{ display: Blogin ? "block" : "none" }}>
            {Bsignined ? (
              <>
                <p>You have signed in Bilibili!</p>
                <Button
                  onClick={bilibiliLogout}
                  icon={
                    <img
                      src="https://plugins.jetbrains.com/files/18850/221952/icon/pluginIcon.png"
                      alt="bilibili icon"
                      width={20}
                    ></img>
                  }
                  size="large"
                >
                  Bilibili Sign out
                </Button>
              </>
            ) : (
              <>
                <QRCode
                  errorLevel="H"
                  value={QR}
                  icon="https://plugins.jetbrains.com/files/18850/221952/icon/pluginIcon.png"
                  style={{ margin: "auto" }}
                />
                <p>{Bprompt}</p>
              </>
            )}
          </div>
        </div>
        <div>
          <img src="images/arrow.gif" alt="arrow" width="100%" height="200" />
        </div>
        <div
          className="app-login"
          onMouseEnter={() => setYlogin(true)}
          onMouseLeave={() => setYlogin(false)}
        >
          <img
            src="images/youtube.png"
            alt="Youtube"
            className="logoimg"
            style={{ display: Ylogin ? "none" : "block" }}
          />
          <div style={{ display: Ylogin ? "block" : "none" }}>
            {Ysignined ? (
              <>
                <p>You have signed in Youtube!</p>
                <Button
                  onClick={googleLogout}
                  icon={
                    <img
                      src="images/YIC.png"
                      alt="youtube icon"
                      width={20}
                    ></img>
                  }
                  size="large"
                >
                  Youtube Sign out
                </Button>
              </>
            ) : (
              <Button
                onClick={googleLogin}
                icon={
                  <img src="images/YIC.png" alt="youtube icon" width={20}></img>
                }
                size="large"
              >
                Youtube Login
              </Button>
            )}
          </div>
        </div>
      </div>
      {Bsignined && Ysignined ? (
        <h3>Choose the role and begin Transfer!</h3>
      ) : (
        <h3>Please login both account first</h3>
      )}
      <Button
        disabled={Bsignined && Ysignined ? false : true}
        size="large"
        onClick={() => (window.location.href = "/B2YUploader")}
      >
        Transfer as uploader
      </Button>
      <Button
        disabled={Bsignined && Ysignined ? false : true}
        size="large"
        onClick={() => (window.location.href = "/B2YViewer")}
      >
        Transfer as viewer
      </Button>
      <FloatButton
        icon={<QuestionCircleOutlined />}
        type="primary"
        style={{
          right: 94,
        }}
      />
    </div>
  );
}
