import "./styles/App.css";
import React, { useState } from "react";
import { Login } from "./components/Login";
import { B2YUploader } from "./components/B2YUploader";
import { Routes, Route, BrowserRouter } from "react-router-dom";
import { Navigate } from "react-router-dom";
import { B2YViewer } from "./components/B2YViewer";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/B2YUploader" element={<B2YUploader />} />
        <Route path="/B2YViewer" element={<B2YViewer />} />
        <Route path="/login" element={<Login />} />
        <Route path="/*" element={<Navigate replace to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
