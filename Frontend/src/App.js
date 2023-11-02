import "./styles/App.css";
import React, { useState } from "react";
import { Login } from "./components/Login";
import { B2YUploader } from "./components/B2YUploader";
import { Routes, Route, BrowserRouter } from "react-router-dom";
import { Navigate } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/main" element={<B2YUploader />} />
        <Route path="/login" element={<Login />} />
        <Route path="/*" element={<Navigate replace to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
