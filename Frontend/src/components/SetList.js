import "../styles/App.css";
import { LikeOutlined, MessageOutlined, StarOutlined } from "@ant-design/icons";
import React from "react";
import { useState, useEffect } from "react";
import { List, Space, Checkbox } from "antd";

export function SetList(props) {
  const { totalV, data, setCheckSet, idx, checkedVideo, uniqueID } = props;
  const [checkVideoList, setCheckVideoList] = useState([]);
  const checkAllVideo =
    data.video_ids.filter((e) => checkedVideo.includes(e)).length ===
      checkVideoList.length && checkVideoList.length !== 0;
  const onCheckAllChange = (e) => {
    totalV
      .filter((e) => data.video_ids.includes(e.id))
      .forEach((t) => {
        let ele = document.getElementById(uniqueID + t.id);
        if (e.target.checked) {
          if (!ele.checked) ele.click();
        } else {
          if (ele.checked) ele.click();
        }
      });
  };
  const IconText = ({ icon, text }) => (
    <Space>
      {React.createElement(icon)}
      {text}
    </Space>
  );

  useEffect(() => {
    setCheckSet((arr) => {
      let tmp = [...arr];
      tmp[idx] = checkVideoList;
      return tmp;
    });
  }, [checkVideoList, idx, setCheckSet]);

  return (
    <List
      itemLayout="vertical"
      size="large"
      pagination={{
        pageSize: 3,
      }}
      dataSource={totalV.filter((e) => data.video_ids.includes(e.id))}
      footer={
        <>
          <Checkbox onChange={onCheckAllChange} checked={checkAllVideo}>
            Check all
          </Checkbox>
          Total {data.video_ids.length} videos
        </>
      }
      renderItem={(item) => (
        <List.Item
          key={item.title}
          actions={[
            <IconText
              icon={StarOutlined}
              text="156"
              key="list-vertical-star-o"
            />,
            <IconText
              icon={LikeOutlined}
              text="156"
              key="list-vertical-like-o"
            />,
            <IconText
              icon={MessageOutlined}
              text="2"
              key="list-vertical-message"
            />,
          ]}
          extra={
            <>
              <img width={250} src={item.img} alt="alt" /> <br></br>
              <Checkbox
                style={{ marginLeft: "180px" }}
                id={uniqueID + item.id}
                disabled={!checkedVideo.includes(item.id)}
                onChange={(e) => {
                  e.target.checked
                    ? setCheckVideoList((arr) => [...arr, item.id])
                    : setCheckVideoList((arr) =>
                        arr.filter((i) => i !== item.id)
                      );
                }}
              >
                check
              </Checkbox>
            </>
          }
        >
          <List.Item.Meta title={item.title} description={item.desc} />
        </List.Item>
      )}
    />
  );
}
