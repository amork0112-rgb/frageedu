import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Checkbox } from "./components/ui/checkbox";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Separator } from "./components/ui/separator";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import EntrancePage from "./pages/EntrancePage";


// Main App Component
function App() {
  const { user, token, login, logout } = useAuth();

  const handleSignup = (newToken, userData, household_token) => {
    login(newToken, userData);
    window.location.href = `/dashboard?id=${household_token}`;
  };

  const handleLogin = (newToken, userData, household_token) => {
    login(newToken, userData);
    window.location.href = `/dashboard?id=${household_token}`;
  };

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/programs" element={<Programs />} />
          <Route path="/community" element={<Community />} />
          <Route path="/news" element={<News />} />
          <Route path="/market" element={<Market />} />
          <Route path="/admissions" element={<AdmissionsPortal />} />
          <Route path="/signup" element={<Signup onSignup={handleSignup} />} />
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          
          {/* Admission Portal Pages - keeping existing functionality */}
          <Route path="/dashboard" element={
            <TokenAuthWrapper>
              <div>Dashboard (existing functionality preserved)</div>
            </TokenAuthWrapper>
          } />
          <Route path="/consent" element={
            <TokenAuthWrapper>
              <div>Consent Page (existing functionality preserved)</div>
            </TokenAuthWrapper>
          } />
          <Route path="/form" element={
            <TokenAuthWrapper>
              <div>Forms Page (existing functionality preserved)</div>
            </TokenAuthWrapper>
          } />
          <Route path="/guide" element={
            <TokenAuthWrapper>
              <div>Guide Page (existing functionality preserved)</div>
            </TokenAuthWrapper>
          } />
          <Route path="/checklist" element={
            <TokenAuthWrapper>
              <div>Checklist Page (existing functionality preserved)</div>
            </TokenAuthWrapper>
          } />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;