import "../styles/App.css";
import { LikeOutlined, MessageOutlined, StarOutlined } from "@ant-design/icons";
import React from "react";
import { List, Space, Checkbox } from "antd";

export function VideoList(props) {
  const { data, checkVideoList, setCheckVideoList } = props;
  const checkAllVideo =
    data.filter((e) => e.disable === false).length === checkVideoList.length &&
    checkVideoList.length !== 0;
  const onCheckAllChange = (e) => {
    data.forEach((t) => {
      if (e.target.checked) {
        if (!checkVideoList.includes(t.id) && t.disable === false)
          setCheckVideoList((arr) => [...arr, t.id]);
      } else {
        if (checkVideoList.includes(t.id) && t.disable === false)
          setCheckVideoList((arr) => arr.filter((i) => i !== t.id));
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
          Total {data.filter((e) => e.disable === false).length} videos
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
                onChange={(e) =>
                  e.target.checked
                    ? setCheckVideoList((arr) => [...arr, item.id])
                    : setCheckVideoList((arr) =>
                        arr.filter((i) => i !== item.id)
                      )
                }
                checked={checkVideoList.includes(item.id) || item.checked}
                disabled={item.disable}
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
