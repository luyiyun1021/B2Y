import "../styles/App.css";
import { LikeOutlined, MessageOutlined, StarOutlined } from "@ant-design/icons";
import React from "react";
import { useState, useEffect } from "react";
import { List, Space, Checkbox } from "antd";

export function SetList(props) {
  const { totalV, data, setCheckSet, idx, checkedVideo } = props;
  const [checkVideoList, setCheckVideoList] = useState([]);
  const checkAllVideo =
    checkVideoList.length !== 0 &&
    totalV.filter(
      (e) =>
        data.video_ids.includes(e.id) &&
        ((e.disable === false && checkedVideo.includes(e.id)) ||
          e.checked === true)
    ).length === checkVideoList.length;
  const onCheckAllChange = (e) => {
    data.video_ids.forEach((t) => {
      if (e.target.checked) {
        if (
          !checkVideoList.includes(t) &&
          // checkedVideo.includes(t) &&
          totalV.filter(
            (e) => e.id === t && (e.disable === false || e.checked === true)
          ).length !== 0
        )
          setCheckVideoList((arr) => [...arr, t]);
      } else {
        if (
          checkVideoList.includes(t) &&
          totalV.filter(
            (e) => e.id === t && (e.disable === false || e.checked === true)
          ).length !== 0
        )
          setCheckVideoList((arr) => arr.filter((i) => i !== t));
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
          Total{" "}
          {
            totalV.filter(
              (e) =>
                data.video_ids.includes(e.id) &&
                (e.disable === false || e.checked === true)
            ).length
          }{" "}
          videos
        </>
      }
      renderItem={(item) => (
        <List.Item
          key={item.title}
          actions={[
            <IconText
              icon={StarOutlined}
              text={item.star}
              key="list-vertical-star-o"
            />,
            <IconText
              icon={LikeOutlined}
              text={item.like}
              key="list-vertical-like-o"
            />,
            <IconText
              icon={MessageOutlined}
              text={item.comment}
              key="list-vertical-message"
            />,
          ]}
          extra={
            <>
              <img width={250} src={item.img} alt="alt" /> <br></br>
              <Checkbox
                style={{ marginLeft: "180px" }}
                disabled={
                  item.checked
                    ? false
                    : !checkedVideo.includes(item.id) || item.disable
                }
                onChange={(e) => {
                  e.target.checked
                    ? setCheckVideoList((arr) => [...arr, item.id])
                    : setCheckVideoList((arr) =>
                        arr.filter((i) => i !== item.id)
                      );
                }}
                checked={checkVideoList.includes(item.id)}
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
