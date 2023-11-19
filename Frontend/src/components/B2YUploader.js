import "../styles/App.css";
import React, { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";
import { Collapse, Avatar, Button, Popconfirm, Col, Row, Spin } from "antd";
import { VideoList } from "./VideoList";
import { SetList } from "./SetList";
import { RollbackOutlined } from "@ant-design/icons";

// let data = {
//   videos: [
//     {
//       id: "BV1LC4y1Z7Li",
//       bvid: "BV1LC4y1Z7Li",
//       aid: 789284286,
//       cid: 1291466320,
//       title: "Foggy Brown",
//       desc: "Bronw University Main Green on a foggy data",
//       img: "http://i2.hdslb.com/bfs/archive/4632e780d3411dccd8fd6758e7d39968449cebf5.jpg",
//       owner_mid: 1794123514,
//       owner_name: "robertmin96",
//       view: 6,
//       like: 0,
//       star: 0,
//       share: 0,
//       comment: 1,
//       disable: true,
//       checked: true,
//     },
//     {
//       id: "BV1y8411C7Mw",
//       bvid: "BV1y8411C7Mw",
//       aid: 234207717,
//       cid: 1285040206,
//       title: "Tennis Practice",
//       desc: "I played tennis with friend in summer 2023",
//       img: "http://i0.hdslb.com/bfs/archive/917f7d98f73cb7af240dacc6bdfe160ff60c1c31.jpg",
//       owner_mid: 1794123514,
//       owner_name: "robertmin96",
//       view: 7,
//       like: 0,
//       star: 0,
//       share: 1,
//       comment: 0,
//       disable: false,
//       checked: false,
//     },
//   ],
//   sets: [
//     {
//       id: 3737408,
//       title: "list3",
//       video_ids: ["BV1LC4y1Z7Li"],
//     },
//     {
//       id: 3737407,
//       title: "list2",
//       video_ids: ["BV1y8411C7Mw"],
//     },
//     {
//       id: 3670927,
//       title: "list1",
//       video_ids: ["BV1LC4y1Z7Li", "BV1y8411C7Mw"],
//     },
//   ],
// };

export function B2YUploader() {
  const [data, setData] = useState(null);
  useEffect(() => {
    const fetchData = async () => {
      await fetch(
        `http://localhost:8000/B2Y/uploader?SESSDATA=${sessionStorage.getItem(
          "SESSDATA"
        )}&access_token=${sessionStorage.getItem("access_token")}`,
        { method: "get" }
      )
        .then(async (res) => await res.json())
        .then((json) => {
          let data = json.data;
          if (data.videos === null) data.videos = [];
          if (data.sets === null) data.sets = [];
          setData(data);
          setCheckSetList(Array(data.sets.length).fill([]));
        });
    };
    fetchData();
  }, []);

  const [checkVideoList, setCheckVideoList] = useState([]);
  const [checkSetList, setCheckSetList] = useState(
    // Array(data.sets.length).fill([])
    []
  );

  const confirm = async () => {
    await fetch(
      `http://localhost:8000/B2Y/migrate_uploader?SESSDATA=${sessionStorage.getItem(
        "SESSDATA"
      )}&access_token=${sessionStorage.getItem("access_token")}`,
      {
        method: "post",
        body: JSON.stringify({
          videos: checkVideoList,
          sets: checkSetList.map((e, i) => ({
            setid: data.sets[i].id,
            videos: e,
          })),
        }),
      }
    )
      .then(async (res) => await res.json())
      .then((data) => {
        if (data.status === "success") {
          alert("Migration Successed!");
        } else {
          alert("Migration Failed!");
        }
      });
  };

  if (
    sessionStorage.getItem("SESSDATA") == null ||
    sessionStorage.getItem("access_token") == null
    // false
  ) {
    return <Navigate replace to="/login" />;
  } else {
    if (data === null)
      return (
        <div style={{ top: "48%", left: "48%", position: "fixed" }}>
          <Spin size="large"></Spin>
        </div>
      );
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
              src={data.b_user_profile}
            />
            <p>{data.b_user_name}</p>
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
                  {/* //TODO make accurate */}
                  <p>
                    <b>Once the migration operation is confirmed,</b>
                  </p>
                  <p>
                    <b>it cannot be stopped.</b>
                  </p>
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
                  <p>
                    <b>Once the migration operation is confirmed,</b>
                  </p>
                  <p>
                    <b>it cannot be stopped.</b>
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
              src={data.y_user_profile}
            />
            <p>{data.y_user_name}</p>
          </Col>
        </Row>

        <div>
          <Collapse
            // defaultActiveKey={["0"]}
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
                  ></VideoList>
                ),
              },
            ]}
          />
          <Collapse
            // defaultActiveKey={["0"]}
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
                            totalV={data.videos}
                            data={e}
                            setCheckSet={setCheckSetList}
                            idx={i}
                            checkedVideo={checkVideoList}
                          ></SetList>
                        ),
                      },
                    ]}
                  />
                )),
              },
            ]}
          />
          <button onClick={() => console.log(checkVideoList)}>click me1</button>
          <button onClick={() => console.log(checkSetList)}>click me2</button>
        </div>
      </div>
    );
  }
}
