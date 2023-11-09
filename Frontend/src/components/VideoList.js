import "../styles/App.css";
import { LikeOutlined, MessageOutlined, StarOutlined } from "@ant-design/icons";
import React from "react";
import { List, Space, Checkbox } from "antd";

export function VideoList(props) {
  const { data, checkVideoList, setCheckVideoList, uniqueID } = props;
  const checkAllVideo =
    data.filter((e) => e.disable === false).length === checkVideoList.length &&
    checkVideoList.length !== 0;
  const onCheckAllChange = (e) => {
    data.forEach((t) => {
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

  return (
    <List
      itemLayout="vertical"
      size="large"
      pagination={{
        pageSize: 3,
      }}
      dataSource={data}
      footer={
        <>
          <Checkbox onChange={onCheckAllChange} checked={checkAllVideo}>
            Check all
          </Checkbox>
          Total {data.length} videos
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
              <img width={250} src={item.img} alt={item.img} /> <br></br>
              <Checkbox
                style={{ marginLeft: "180px" }}
                id={uniqueID + item.id}
                onChange={(e) =>
                  e.target.checked
                    ? setCheckVideoList((arr) => [...arr, item.id])
                    : setCheckVideoList((arr) =>
                        arr.filter((i) => i !== item.id)
                      )
                }
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
