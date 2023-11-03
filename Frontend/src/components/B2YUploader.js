import "../styles/App.css";
import React, { useState } from "react";
import { Navigate } from "react-router-dom";
import { Collapse, Avatar, Button, Popconfirm, Col, Row } from "antd";
import { VideoList } from "./VideoList";
import { SetList } from "./SetList";
import { RollbackOutlined } from "@ant-design/icons";

let youtubeName = "Bob";
let biliName = "Alice";

let data = {
  videos: [
    {
      id: 1,
      title: "hello",
      desc: "!",
      img: "images/youtube.png",
      like: 50,
      star: 100,
      comment: 150,
      disable: false,
      checked: false,
    },
    {
      id: 2,
      title: "world",
      desc: "?",
      img: "images/youtube.png",
      like: 50,
      star: 100,
      comment: 150,
      disable: false,
      checked: false,
    },
  ],
  sets: [
    { id: 1, title: "set1", videoidx: [0] },
    { id: 2, title: "set2", videoidx: [1] },
  ],
};

export function B2YUploader() {
  const [checkVideoList, setCheckVideoList] = useState([]);
  const [checkSetList, setCheckSetList] = useState(
    Array(data.sets.length).fill([])
  );
  const confirm = () =>
    new Promise((resolve) => {
      setTimeout(() => resolve(null), 3000);
    });

  if (
    sessionStorage.getItem("SESSDATA") == null ||
    sessionStorage.getItem("access_token") == null
    // false
  ) {
    return <Navigate replace to="/login" />;
  } else {
    fetch(
      `http://localhost:8000/B2Y/uploader?SESSDATA=${sessionStorage.getItem(
        "SESSDATA"
      )}&access_token=${sessionStorage.getItem("access_token")}`,
      { method: "get" }
    ).then(async (res) => {
      let json = await res.json();
      console.log(json);
    });
    return (
      <div style={{ margin: "2rem" }}>
        <Button
          type="default"
          shape="circle"
          icon={<RollbackOutlined />}
          size={"large"}
          onClick={() => (window.location.href = "/login")}
        ></Button>

        <Row style={{ marginLeft: "auto" }}>
          <Col span={8} style={{ textAlign: "center" }}>
            <Avatar
              size={{ xs: 24, sm: 32, md: 40, lg: 64, xl: 80, xxl: 100 }}
              src="images/bilibili.png"
            />
            <p>{biliName}</p>
          </Col>
          <Col span={8} style={{ textAlign: "center", marginTop: "3rem" }}>
            <Popconfirm
              title="Confirm Transfer"
              placement="bottom"
              description={
                <>
                  <p>
                    Total Video:{" "}
                    {data.videos.filter((e) => e.disable === false).length}
                  </p>
                  <p>Total Set: {data.sets.length}</p>
                </>
              }
              onConfirm={confirm}
            >
              <Button type="dashed" danger size="large">
                Transfer All
              </Button>
            </Popconfirm>
            <Popconfirm
              title="Confirm Transfer"
              placement="bottom"
              description={
                <>
                  <p>Total Video: {checkVideoList.length}</p>
                  <p>
                    Total Set:{" "}
                    {checkSetList.filter((e) => e.length !== 0).length}
                  </p>
                </>
              }
              onConfirm={confirm}
            >
              <Button type="primary" size="large">
                Transfer To
              </Button>
            </Popconfirm>
          </Col>
          <Col span={8} style={{ textAlign: "center" }}>
            <Avatar
              size={{ xs: 24, sm: 32, md: 40, lg: 64, xl: 80, xxl: 100 }}
              src="images/youtube.png"
            />
            <p>{youtubeName}</p>
          </Col>
        </Row>

        <div>
          <Collapse
            defaultActiveKey={["0"]}
            expandIconPosition={"start"}
            items={[
              {
                key: 0,
                label: "Videos",
                children: (
                  <VideoList
                    data={data.videos}
                    checkVideoList={checkVideoList}
                    setCheckVideoList={setCheckVideoList}
                    uniqueID={"0001"}
                  ></VideoList>
                ),
              },
            ]}
          />
          <Collapse
            defaultActiveKey={["0"]}
            expandIconPosition={"start"}
            items={[
              {
                key: 0,
                label: "Sets",
                children: data.sets.map((e, i) => (
                  <Collapse
                    // defaultActiveKey={["0"]}
                    expandIconPosition={"start"}
                    items={[
                      {
                        key: i,
                        label: e.title,
                        children: (
                          <SetList
                            data={e.videoidx.map((i) => data.videos[i])}
                            setCheckSet={setCheckSetList}
                            idx={i}
                            checkedVideo={checkVideoList}
                            uniqueID={"0002"}
                          ></SetList>
                        ),
                      },
                    ]}
                  />
                )),
              },
            ]}
          />
          <button onClick={() => console.log(checkSetList)}>click me1</button>
          <button onClick={() => console.log(checkVideoList)}>click me2</button>
        </div>
      </div>
    );
  }
}
