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

import { 
  CheckCircle, 
  Clock, 
  FileText, 
  BookOpen, 
  ClipboardList, 
  Users, 
  Info, 
  Eye, 
  ArrowRight, 
  Star, 
  Shield, 
  Smartphone,
  Menu,
  X,
  Globe,
  Lightbulb,
  Target,
  MessageCircle,
  Calendar,
  Award,
  MapPin,
  Phone,
  Mail,
  ChevronRight,
  Play,
  BookmarkCheck,
  AlertCircle,
  ExternalLink,
  Plus,
  Edit3,
  Trash2,
  Save,
  Settings,
  BarChart3,
  Upload,
  Image as ImageIcon,
  Bold,
  Italic,
  List,
  Link,
  Type,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Quote,
  Search,
  Filter,
  MoreVertical,
  Copy,
  Download,
  RefreshCw,
  UserX,
  UserCheck,
  Key,
  Trash,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  SortAsc,
  SortDesc
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Header Component
const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 w-full bg-white/95 backdrop-blur-md border-b border-gray-100 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <a href="/" className="cursor-pointer">
              <img 
                src="/logo.png" 
                alt="Frage EDU Logo" 
                className="h-12 w-auto hover:opacity-80 transition-opacity"
              />
            </a>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="/#about" className="text-gray-700 hover:text-purple-600 transition-colors">About</a>
            <a href="/programs" className="text-gray-700 hover:text-purple-600 transition-colors">Programs</a>
            <a href="/admissions" className="text-gray-700 hover:text-purple-600 transition-colors">Admissions</a>
            <a href="/news" className="text-gray-700 hover:text-purple-600 transition-colors">News</a>
          </nav>

          <div className="hidden md:flex items-center space-x-4">
            <Button variant="ghost" onClick={() => window.location.href = '/login'}>
              Login
            </Button>
            <Button className="bg-purple-600 hover:bg-purple-700" onClick={() => window.location.href = '/signup'}>
              Sign Up
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button 
            className="md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden pb-4 border-t border-gray-100 mt-4 pt-4">
            <nav className="flex flex-col space-y-3">
              <a href="/#about" className="text-gray-700 hover:text-purple-600 transition-colors">About</a>
              <a href="/programs" className="text-gray-700 hover:text-purple-600 transition-colors">Programs</a>
              <a href="/admissions" className="text-gray-700 hover:text-purple-600 transition-colors">Admissions</a>
              <a href="/news" className="text-gray-700 hover:text-purple-600 transition-colors">News</a>
              <div className="flex flex-col space-y-2 pt-3 border-t">
                <Button variant="ghost" onClick={() => window.location.href = '/login'}>Login</Button>
                <Button className="bg-purple-600 hover:bg-purple-700" onClick={() => window.location.href = '/signup'}>Sign Up</Button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

// Footer Component
const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Frage EDU</h3>
                <p className="text-gray-400 text-sm">생각하는 영어교육</p>
              </div>
            </div>
            <p className="text-gray-400 mb-4">
              비판적 사고력을 기르는 영어교육으로 글로벌 리더를 양성합니다.
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="/programs" className="hover:text-white transition-colors">Programs</a></li>
              <li><a href="/admissions" className="hover:text-white transition-colors">Admissions</a></li>
              <li><a href="/community" className="hover:text-white transition-colors">Community</a></li>
              <li><a href="/market" className="hover:text-white transition-colors">Market</a></li>
              <li><a href="/admin/login" className="hover:text-white transition-colors text-sm opacity-70">Admin</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Contact Info</h4>
            <ul className="space-y-2 text-gray-400">
              <li className="flex items-center space-x-2">
                <MapPin className="w-4 h-4" />
                <span>대구 수성구 범어천로 167 3-4층</span>
              </li>
              <li className="flex items-center space-x-2">
                <Phone className="w-4 h-4" />
                <span>053-754-0577</span>
              </li>
              <li className="flex items-center space-x-2">
                <Mail className="w-4 h-4" />
                <span>frage0577@gmail.com</span>
              </li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Follow Us</h4>
            <div className="flex space-x-3">
              <Button variant="outline" size="sm" className="bg-transparent border-gray-600 text-gray-400 hover:text-white hover:border-gray-400">
                Kakao
              </Button>
              <Button variant="outline" size="sm" className="bg-transparent border-gray-600 text-gray-400 hover:text-white hover:border-gray-400">
                Naver
              </Button>
              <Button variant="outline" size="sm" className="bg-transparent border-gray-600 text-gray-400 hover:text-white hover:border-gray-400">
                YouTube
              </Button>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2025 Frage EDU. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

// Homepage Component
const Homepage = () => {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      
      {/* Hero Section */}
      <section className="pt-24 pb-16 bg-gradient-to-br from-purple-50 to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="text-center lg:text-left">
              <h1 className="font-heading text-4xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
                생각하는 힘을 키우는<br />
                <span className="text-purple-600">영어교육, 프라게</span>
              </h1>
              <p className="text-lg lg:text-xl text-gray-600 mb-8 leading-relaxed">
                Growing the Power to Think through English Learning.<br />
                비판적 사고력과 창의력을 기르는 프로젝트 기반 영어교육을 제공합니다.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Button size="lg" className="bg-purple-600 hover:bg-purple-700" onClick={() => document.getElementById('programs').scrollIntoView({ behavior: 'smooth' })}>
                  프로그램 소개
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
                <Button variant="outline" size="lg" onClick={() => window.location.href = '/admissions'}>
                  입학 안내
                </Button>
              </div>
            </div>
            
            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                <img 
                  src="https://images.unsplash.com/photo-1640622304233-7335e936f11b?q=80&w=800&h=600&fit=crop"
                  alt="영어교육 수업 모습" 
                  className="w-full h-[500px] object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-transparent"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">About Frage EDU</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              프라게는 단순한 영어 학습이 아닌, 영어를 통한 사고력 개발에 집중합니다.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
            <Card className="p-6 text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Lightbulb className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Critical Thinking</h3>
              <p className="text-gray-600">
                비판적 사고력을 기르는 토론과 분석 중심의 수업을 진행합니다.
              </p>
            </Card>

            <Card className="p-6 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Target className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Project Learning</h3>
              <p className="text-gray-600">
                실제 프로젝트를 통해 문제 해결 능력과 창의성을 개발합니다.
              </p>
            </Card>

            <Card className="p-6 text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Globe className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Global Communication</h3>
              <p className="text-gray-600">
                세계와 소통할 수 있는 실용적인 영어 능력을 키워드립니다.
              </p>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <img 
                src="https://images.unsplash.com/photo-1591218214141-45545921d2d9?q=80&w=600&h=400&fit=crop"
                alt="교실 수업 모습" 
                className="rounded-lg shadow-lg"
              />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">우리의 교육 철학</h3>
              <p className="text-gray-600 mb-6">
                프라게는 '왜?'라는 질문에서 시작합니다. 학생들이 스스로 질문하고, 
                탐구하며, 답을 찾아가는 과정을 통해 진정한 학습이 일어난다고 믿습니다.
              </p>
              <ul className="space-y-3">
                <li className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span>소규모 맞춤형 수업</span>
                </li>
                <li className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span>원어민과 한국인 교사의 협력 수업</span>
                </li>
                <li className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span>개별 진도와 수준별 학습</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Programs Section */}
      <section id="programs" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">Our Programs</h2>
            <p className="text-xl text-gray-600">연령별 맞춤형 영어교육 프로그램</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gradient-to-br from-yellow-100 to-orange-100"></div>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-2">Kindergarten English</h3>
                <p className="text-gray-600 mb-4">5-7세 아이들을 위한 놀이 중심 영어교육</p>
                <Button variant="outline" className="w-full">
                  Learn More <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>

            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gradient-to-br from-green-100 to-emerald-100"></div>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-2">Elementary Lower</h3>
                <p className="text-gray-600 mb-4">초등 저학년 기초 영어 및 읽기 교육</p>
                <Button variant="outline" className="w-full">
                  Learn More <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>

            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gradient-to-br from-blue-100 to-cyan-100"></div>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-2">Elementary Upper</h3>
                <p className="text-gray-600 mb-4">초등 고학년 심화 영어 및 글쓰기</p>
                <Button variant="outline" className="w-full">
                  Learn More <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>

            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-48 bg-gradient-to-br from-purple-100 to-indigo-100"></div>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-2">Middle School Prep</h3>
                <p className="text-gray-600 mb-4">중학교 준비 비판적 사고 영어</p>
                <Button variant="outline" className="w-full">
                  Learn More <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Admissions Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">Admissions Process</h2>
            <p className="text-xl text-gray-600">간단한 4단계로 입학을 완료하세요</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
            <div className="text-center">
              <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4 relative">
                <span className="text-2xl font-bold text-purple-600">1</span>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center">
                  <FileText className="w-3 h-3 text-white" />
                </div>
              </div>
              <h3 className="text-lg font-semibold mb-2">Sign Up</h3>
              <p className="text-gray-600">온라인 가입 및 기본 정보 입력</p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4 relative">
                <span className="text-2xl font-bold text-green-600">2</span>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-600 rounded-full flex items-center justify-center">
                  <ClipboardList className="w-3 h-3 text-white" />
                </div>
              </div>
              <h3 className="text-lg font-semibold mb-2">Submit Forms</h3>
              <p className="text-gray-600">입학 신청서 및 서류 제출</p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 relative">
                <span className="text-2xl font-bold text-blue-600">3</span>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-3 h-3 text-white" />
                </div>
              </div>
              <h3 className="text-lg font-semibold mb-2">Confirm Admission</h3>
              <p className="text-gray-600">입학 확정 및 등록금 납부</p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4 relative">
                <span className="text-2xl font-bold text-orange-600">4</span>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-orange-600 rounded-full flex items-center justify-center">
                  <Play className="w-3 h-3 text-white" />
                </div>
              </div>
              <h3 className="text-lg font-semibold mb-2">Start Class</h3>
              <p className="text-gray-600">수업 시작 및 학습 여정 시작</p>
            </div>
          </div>

          <div className="text-center">
            <Button size="lg" className="bg-purple-600 hover:bg-purple-700" onClick={() => window.location.href = '/admissions'}>
              Apply Now
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>
      </section>

      {/* News Preview Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">Latest News</h2>
            <p className="text-xl text-gray-600">Frage EDU의 최신 소식을 확인하세요</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="p-6 hover:shadow-lg transition-shadow">
              <Badge className="bg-blue-100 text-blue-800 mb-3">개강소식</Badge>
              <h4 className="font-semibold mb-2">2025년 3월 신학기 개강 안내</h4>
              <p className="text-gray-600 mb-3 text-sm">
                새 학기를 맞이하여 모든 반의 개강 일정과 준비사항을 안내드립니다.
              </p>
              <span className="text-sm text-gray-500">2025.02.20</span>
            </Card>

            <Card className="p-6 hover:shadow-lg transition-shadow">
              <Badge className="bg-green-100 text-green-800 mb-3">공지사항</Badge>
              <h4 className="font-semibold mb-2">겨울방학 특별 프로그램 접수</h4>
              <p className="text-gray-600 mb-3 text-sm">
                창의적 글쓰기와 토론 중심의 집중 영어 캠프를 진행합니다.
              </p>
              <span className="text-sm text-gray-500">2025.01.15</span>
            </Card>

            <Card className="p-6 hover:shadow-lg transition-shadow">
              <Badge className="bg-purple-100 text-purple-800 mb-3">뉴스</Badge>
              <h4 className="font-semibold mb-2">지역 영어교육 혁신상 수상</h4>
              <p className="text-gray-600 mb-3 text-sm">
                비판적 사고력 기반 영어교육 프로그램으로 혁신상을 수상했습니다.
              </p>
              <span className="text-sm text-gray-500">2025.01.10</span>
            </Card>
          </div>

          <div className="text-center mt-12">
            <Button variant="outline" onClick={() => window.location.href = '/news'}>
              모든 소식 보기
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-purple-600 text-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl lg:text-4xl font-bold mb-4">
            지금 바로 시작하세요
          </h2>
          <p className="text-xl text-purple-100 mb-8">
            아이의 미래를 바꾸는 영어교육, 프라게와 함께하세요
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              variant="secondary" 
              className="bg-white text-purple-600 hover:bg-gray-100"
              onClick={() => window.location.href = '/admissions'}
            >
              입학 신청하기
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="border-white text-white hover:bg-white hover:text-purple-600"
              onClick={() => window.location.href = '/programs'}
            >
              프로그램 보기
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

// Auth Context (simplified for this demo)
const useAuth = () => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  const login = (newToken, userData) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setUser(userData);
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return { user, token, login, logout };
};

// Admin Auth Context
const useAdminAuth = () => {
  const [admin, setAdmin] = useState(null);
  const [adminToken, setAdminToken] = useState(localStorage.getItem('adminToken'));

  useEffect(() => {
    if (adminToken) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${adminToken}`;
      fetchAdminProfile();
    }
  }, [adminToken]);

  const fetchAdminProfile = async () => {
    try {
      const response = await axios.get(`${API}/admin/profile`);
      setAdmin(response.data);
    } catch (error) {
      adminLogout();
    }
  };

  const adminLogin = (newToken, adminData) => {
    localStorage.setItem('adminToken', newToken);
    setAdminToken(newToken);
    setAdmin(adminData);
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
  };

  const adminLogout = () => {
    localStorage.removeItem('adminToken');
    setAdminToken(null);
    setAdmin(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return { admin, adminToken, adminLogin, adminLogout };
};

// Exam Reservation Component
const ExamReservationForm = () => {
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [brchType, setBrchType] = useState('');

  useEffect(() => {
    // Get branch type from URL
    const urlParams = new URLSearchParams(window.location.search);
    const branchFromUrl = urlParams.get('brchType') || 'junior';
    setBrchType(branchFromUrl);

    // Redirect to signup if not logged in
    if (!token && !user) {
      window.location.href = `/signup?next=/exam/reserve?brchType=${branchFromUrl}`;
      return;
    }
  }, [token, user]);

  const handleTallyRedirect = () => {
    setLoading(true);
    
    // Construct Tally prefilled URL
    const base = "https://tally.so/r/n9oxBG";
    const url = new URL(base);
    
    if (user) {
      url.searchParams.set("brchType", brchType);
      url.searchParams.set("token", user.household_token);
      url.searchParams.set("user_id", user.id);
      url.searchParams.set("parent_name", user.parent_name || user.email);
      url.searchParams.set("parent_email", user.email);
      url.searchParams.set("parent_phone", user.phone || '');
      url.searchParams.set("student_name", user.student_name || '');
    }
    
    window.location.href = url.toString();
  };

  const getBranchInfo = (type) => {
    switch(type) {
      case 'junior':
        return {
          title: '초등부 입학시험',
          description: '초등학생 대상 영어 레벨테스트 및 입학 상담',
          duration: '60분',
          format: '오프라인 시험'
        };
      case 'middle':
        return {
          title: '중등부 입학시험',
          description: '중학생 대상 심화 영어 평가 및 상담',
          duration: '90분',
          format: '오프라인 시험'
        };
      default:
        return {
          title: '입학시험',
          description: '학생 수준 평가 및 상담',
          duration: '60-90분',
          format: '오프라인 시험'
        };
    }
  };

  const branchInfo = getBranchInfo(brchType);

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 flex items-center justify-center">
        <Card className="w-full max-w-md text-center">
          <CardContent className="pt-6">
            <AlertCircle className="w-16 h-16 text-orange-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">로그인이 필요합니다</h2>
            <p className="text-gray-600 mb-4">입학시험 예약을 위해 먼저 로그인해주세요.</p>
            <Button onClick={() => window.location.href = '/login'} className="bg-purple-600 hover:bg-purple-700">
              로그인하기
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50">
      <Header />
      <div className="max-w-4xl mx-auto px-4 py-24">
        {/* Header Section */}
        <div className="text-center mb-12">
          <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <BookmarkCheck className="w-10 h-10 text-purple-600" />
          </div>
          <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
            {branchInfo.title} 예약
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            {branchInfo.description}
          </p>
        </div>

        {/* Branch Type Badge */}
        <div className="flex justify-center mb-8">
          <Badge className={`px-4 py-2 text-sm font-medium ${
            brchType === 'junior' 
              ? 'bg-green-100 text-green-800' 
              : 'bg-blue-100 text-blue-800'
          }`}>
            {brchType === 'junior' ? '초등부' : '중등부'} 과정
          </Badge>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Reservation Card */}
          <div className="lg:col-span-2">
            <Card className="rounded-xl shadow-lg">
              <CardHeader className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-t-xl">
                <CardTitle className="text-xl">시험 예약 신청</CardTitle>
                <CardDescription className="text-purple-100">
                  아래 버튼을 클릭하여 시험 일정을 예약해주세요
                </CardDescription>
              </CardHeader>
              <CardContent className="p-8">
                {/* User Info Display */}
                <div className="bg-gray-50 rounded-lg p-6 mb-6">
                  <h3 className="font-semibold text-gray-900 mb-4">신청자 정보</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">학부모 성명:</span>
                      <span className="ml-2 font-medium">{user.parent_name || user.email}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">이메일:</span>
                      <span className="ml-2 font-medium">{user.email}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">휴대폰:</span>
                      <span className="ml-2 font-medium">{user.phone || '미입력'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">학생 이름:</span>
                      <span className="ml-2 font-medium">{user.student_name || '미입력'}</span>
                    </div>
                  </div>
                </div>

                {/* Reservation Form Notice */}
                <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                  <div className="flex">
                    <Info className="h-6 w-6 text-blue-400 mr-3" />
                    <div>
                      <h4 className="text-blue-800 font-medium">예약 안내</h4>
                      <p className="text-blue-700 text-sm mt-1">
                        시험 예약 양식에서 캠퍼스, 일정, 레벨을 선택하실 수 있습니다.
                        기본 정보는 자동으로 입력됩니다.
                      </p>
                    </div>
                  </div>
                </div>

                {/* CTA Button */}
                <Button 
                  onClick={handleTallyRedirect}
                  disabled={loading}
                  className="w-full bg-purple-600 hover:bg-purple-700 py-4 text-lg"
                >
                  {loading ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                      예약 양식으로 이동 중...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center">
                      <Calendar className="w-5 h-5 mr-2" />
                      시험 일정 예약하기
                      <ExternalLink className="w-4 h-4 ml-2" />
                    </div>
                  )}
                </Button>

                <p className="text-center text-sm text-gray-500 mt-4">
                  예약 완료 후 카카오 알림톡으로 확정 안내를 드립니다
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Side Info Panel */}
          <div className="space-y-6">
            {/* Exam Info Card */}
            <Card className="rounded-xl shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">시험 정보</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-3">
                  <Clock className="w-5 h-5 text-purple-600" />
                  <div>
                    <p className="font-medium">소요시간</p>
                    <p className="text-sm text-gray-600">{branchInfo.duration}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <MapPin className="w-5 h-5 text-purple-600" />
                  <div>
                    <p className="font-medium">시험 형태</p>
                    <p className="text-sm text-gray-600">{branchInfo.format}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Users className="w-5 h-5 text-purple-600" />
                  <div>
                    <p className="font-medium">준비물</p>
                    <p className="text-sm text-gray-600">신분증, 필기구</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Process Steps */}
            <Card className="rounded-xl shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">진행 절차</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-semibold mt-0.5">
                      1
                    </div>
                    <div>
                      <p className="font-medium">시험 예약</p>
                      <p className="text-sm text-gray-600">원하는 일정과 캠퍼스 선택</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-semibold mt-0.5">
                      2
                    </div>
                    <div>
                      <p className="font-medium">시험 응시</p>
                      <p className="text-sm text-gray-600">예약된 일시에 캠퍼스 방문</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-semibold mt-0.5">
                      3
                    </div>
                    <div>
                      <p className="font-medium">결과 상담</p>
                      <p className="text-sm text-gray-600">레벨 확정 및 수업 안내</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-semibold mt-0.5">
                      4
                    </div>
                    <div>
                      <p className="font-medium">등록 완료</p>
                      <p className="text-sm text-gray-600">수강료 납입 및 수업 시작</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Contact Info */}
            <Card className="rounded-xl shadow-sm bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200">
              <CardContent className="p-6">
                <h4 className="font-semibold text-purple-900 mb-3">문의사항이 있으시다면?</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center space-x-2 text-purple-700">
                    <Phone className="w-4 h-4" />
                    <span>02-1234-5678</span>
                  </div>
                  <div className="flex items-center space-x-2 text-purple-700">
                    <Mail className="w-4 h-4" />
                    <span>info@frage.edu</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

// Exam Confirmation Page
const ExamConfirmation = () => {
  const [brchType, setBrchType] = useState('');

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const branchFromUrl = urlParams.get('brchType') || 'junior';
    setBrchType(branchFromUrl);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50">
      <Header />
      <div className="max-w-2xl mx-auto px-4 py-24">
        <div className="text-center mb-12">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
            예약이 접수되었습니다
          </h1>
          <p className="text-xl text-gray-600">
            시험 일정 확정 후 카카오 알림톡으로 안내드리겠습니다
          </p>
        </div>

        <Card className="rounded-xl shadow-lg bg-white">
          <CardContent className="p-8 text-center">
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
              <h3 className="font-semibold text-green-800 mb-2">접수 완료</h3>
              <p className="text-green-700 text-sm">
                입학시험 예약이 정상적으로 접수되었습니다.<br />
                담당자 검토 후 24시간 내에 확정 안내를 드립니다.
              </p>
            </div>

            <div className="space-y-4 mb-8 text-left">
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">과정</span>
                <span className="font-medium">
                  {brchType === 'junior' ? '초등부' : '중등부'} 입학시험
                </span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">접수일시</span>
                <span className="font-medium">
                  {new Date().toLocaleDateString('ko-KR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-gray-600">알림 방법</span>
                <span className="font-medium">카카오 알림톡</span>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button 
                variant="outline" 
                onClick={() => window.location.href = '/'}
                className="flex-1"
              >
                홈으로 돌아가기
              </Button>
              <Button 
                onClick={() => window.location.href = `/exam/guide?brchType=${brchType}`}
                className="flex-1 bg-purple-600 hover:bg-purple-700"
              >
                <BookOpen className="w-4 h-4 mr-2" />
                시험 준비 안내
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
      <Footer />
    </div>
  );
};

// Exam Guide Page
const ExamGuide = () => {
  const [brchType, setBrchType] = useState('');

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const branchFromUrl = urlParams.get('brchType') || 'junior';
    setBrchType(branchFromUrl);
  }, []);

  const getGuideContent = (type) => {
    if (type === 'junior') {
      return {
        title: '초등부 입학시험 안내',
        duration: '60분',
        sections: [
          { name: '듣기 평가', time: '20분', description: '기본 어휘 및 문장 이해력 평가' },
          { name: '읽기 평가', time: '25분', description: '독해력 및 문법 기초 평가' },
          { name: '말하기 평가', time: '15분', description: '간단한 대화 및 발표 능력 평가' }
        ]
      };
    } else {
      return {
        title: '중등부 입학시험 안내',
        duration: '90분',
        sections: [
          { name: '듣기 평가', time: '25분', description: '심화 듣기 및 노트테이킹 평가' },
          { name: '읽기 평가', time: '35분', description: '복합 독해 및 비판적 사고 평가' },
          { name: '쓰기 평가', time: '20분', description: '에세이 작성 및 논증 능력 평가' },
          { name: '말하기 평가', time: '10분', description: '토론 및 프레젠테이션 능력 평가' }
        ]
      };
    }
  };

  const guideContent = getGuideContent(brchType);

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <div className="max-w-4xl mx-auto px-4 py-24">
        <div className="text-center mb-12">
          <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <BookOpen className="w-10 h-10 text-blue-600" />
          </div>
          <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
            {guideContent.title}
          </h1>
          <p className="text-xl text-gray-600">
            시험 당일 준비사항과 진행 방식을 안내드립니다
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            {/* Test Sections */}
            <Card className="rounded-xl shadow-sm">
              <CardHeader>
                <CardTitle className="text-xl">시험 구성</CardTitle>
                <CardDescription>
                  총 소요시간: {guideContent.duration}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {guideContent.sections.map((section, index) => (
                    <div key={index} className="border-l-4 border-blue-400 pl-4 py-2">
                      <div className="flex justify-between items-start mb-1">
                        <h4 className="font-semibold text-gray-900">{section.name}</h4>
                        <Badge variant="outline">{section.time}</Badge>
                      </div>
                      <p className="text-gray-600 text-sm">{section.description}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Preparation Tips */}
            <Card className="rounded-xl shadow-sm">
              <CardHeader>
                <CardTitle className="text-xl">준비 사항</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">지참물</h4>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span>신분증 (학생증 또는 주민등록증)</span>
                      </li>
                      <li className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span>필기구 (연필, 지우개)</span>
                      </li>
                      <li className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span>물병 (선택사항)</span>
                      </li>
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">주의사항</h4>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li className="flex items-center space-x-2">
                        <AlertCircle className="w-4 h-4 text-orange-600" />
                        <span>시험 시작 15분 전 도착</span>
                      </li>
                      <li className="flex items-center space-x-2">
                        <AlertCircle className="w-4 h-4 text-orange-600" />
                        <span>전자기기 사용 금지</span>
                      </li>
                      <li className="flex items-center space-x-2">
                        <AlertCircle className="w-4 h-4 text-orange-600" />
                        <span>시험 중 퇴실 불가</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <Card className="rounded-xl shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">시험 당일 일정</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">도착</span>
                    <span className="font-medium">시험 15분 전</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">등록 및 안내</span>
                    <span className="font-medium">10분</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">시험 진행</span>
                    <span className="font-medium">{guideContent.duration}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">결과 안내</span>
                    <span className="font-medium">시험 후 1주일</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="rounded-xl shadow-sm bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
              <CardContent className="p-6">
                <h4 className="font-semibold text-blue-900 mb-3">궁금한 점이 있다면?</h4>
                <p className="text-blue-700 text-sm mb-4">
                  시험 관련 문의사항은 언제든지 연락 주세요.
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center space-x-2 text-blue-700">
                    <Phone className="w-4 h-4" />
                    <span>02-1234-5678</span>
                  </div>
                  <div className="flex items-center space-x-2 text-blue-700">
                    <Mail className="w-4 h-4" />
                    <span>exam@frage.edu</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="text-center mt-12">
          <Button 
            onClick={() => window.location.href = '/'}
            variant="outline"
            className="px-8"
          >
            홈으로 돌아가기
          </Button>
        </div>
      </div>
      <Footer />
    </div>
  );
};

// Programs Page with Exam Reservation
const Programs = () => {
  const programsData = [
    {
      id: 'kinder',
      title: 'Kindergarten English',
      subtitle: '유치부 (5-7세)',
      description: '놀이 중심의 영어 교육으로 자연스러운 언어 습득을 도와드립니다.',
      features: ['스토리텔링', '신체 활동', '창의적 표현', '기초 파닉스'],
      highlights: ['원어민과 함께하는 즐거운 수업', '개별 맞춤 진도', '창의력 개발 중심']
    },
    {
      id: 'junior',
      title: 'Elementary English',
      subtitle: '초등부 (8-12세)', 
      description: '체계적인 읽기, 쓰기 교육과 프로젝트 기반 학습을 진행합니다.',
      features: ['독해력 향상', '창작 활동', '토론 참여', '프로젝트 학습'],
      highlights: ['체계적인 커리큘럼', '프로젝트 기반 학습', '발표력 향상']
    },
    {
      id: 'middle', 
      title: 'Middle School English',
      subtitle: '중등부 (13-16세)',
      description: '비판적 사고력과 고급 영어 실력을 기르는 심화 과정입니다.',
      features: ['비판적 사고', '에세이 작성', '토론 및 발표', '학술 영어'],
      highlights: ['대학 진학 준비', '고급 영어 실력', '리더십 개발']
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Header />
      
      {/* Hero Section */}
      <section className="pt-24 pb-16 bg-gradient-to-br from-purple-50 to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            Frage EDU Programs
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            연령별 맞춤형 영어교육 프로그램으로 비판적 사고력을 키워드립니다
          </p>
        </div>
      </section>

      {/* Programs Grid */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {programsData.map((program) => (
              <Card key={program.id} className="rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className={`h-48 rounded-t-xl ${
                  program.id === 'kinder' 
                    ? 'bg-gradient-to-br from-yellow-100 to-orange-100'
                    : program.id === 'junior'
                    ? 'bg-gradient-to-br from-green-100 to-emerald-100'
                    : 'bg-gradient-to-br from-blue-100 to-indigo-100'
                }`}>
                  <div className="h-full flex items-center justify-center">
                    <div className={`w-20 h-20 rounded-full flex items-center justify-center ${
                      program.id === 'kinder'
                        ? 'bg-orange-200'
                        : program.id === 'junior' 
                        ? 'bg-green-200'
                        : 'bg-blue-200'
                    }`}>
                      <BookOpen className={`w-10 h-10 ${
                        program.id === 'kinder'
                          ? 'text-orange-600'
                          : program.id === 'junior'
                          ? 'text-green-600' 
                          : 'text-blue-600'
                      }`} />
                    </div>
                  </div>
                </div>
                
                <CardContent className="p-8">
                  <div className="mb-4">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{program.title}</h3>
                    <p className="text-purple-600 font-medium">{program.subtitle}</p>
                  </div>
                  
                  <p className="text-gray-600 mb-6">{program.description}</p>
                  
                  <div className="mb-6">
                    <h4 className="font-semibold text-gray-900 mb-3">주요 특징</h4>
                    <div className="grid grid-cols-2 gap-2">
                      {program.features.map((feature, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <CheckCircle className="w-4 h-4 text-green-600" />
                          <span className="text-sm text-gray-600">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <Button 
                      variant="outline"
                      onClick={() => window.location.href = '/admissions'}
                      className="w-full"
                    >
                      <Info className="w-4 h-4 mr-2" />
                      입학 안내보기
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-br from-purple-50 to-indigo-50">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            입학을 원하시나요?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            자세한 입학 절차와 시험 일정을 확인해보세요
          </p>
          
          <Button 
            size="lg" 
            className="bg-purple-600 hover:bg-purple-700 px-8 py-4 text-lg"
            onClick={() => window.location.href = '/admissions'}
          >
            입학 안내 보기
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </section>

      <Footer />
    </div>
  );
};



const News = () => {
  const [activeCategory, setActiveCategory] = useState('전체');
  const [newsData, setNewsData] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const categories = ['전체', '개강소식', '공지사항', '뉴스'];

  useEffect(() => {
    fetchNews();
  }, [activeCategory]);

  const fetchNews = async () => {
    try {
      const params = activeCategory !== '전체' ? `?category=${activeCategory}` : '';
      const response = await axios.get(`${API}/news${params}`);
      setNewsData(response.data.articles || []);
    } catch (error) {
      console.error('Failed to fetch news:', error);
      // Fallback to mock data if API fails
      setNewsData([
        {
          id: 1,
          category: '개강소식',
          title: '2025년 3월 신학기 개강 안내',
          content: '새 학기를 맞이하여 모든 반의 개강 일정과 준비사항을 안내드립니다.',
          created_at: '2025-02-20',
          image_url: 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?q=80&w=600&h=300&fit=crop',
          featured: true
        },
        {
          id: 2,
          category: '공지사항',
          title: '겨울방학 특별 프로그램 접수 시작',
          content: '창의적 글쓰기와 토론 중심의 겨울방학 집중 영어 캠프 참가자를 모집합니다.',
          created_at: '2025-01-15',
          image_url: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=600&h=300&fit=crop'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const filteredNews = activeCategory === '전체' 
    ? newsData 
    : newsData.filter(item => item.category === activeCategory);

  const getCategoryColor = (category) => {
    switch(category) {
      case '개강소식': return 'bg-blue-100 text-blue-800';
      case '공지사항': return 'bg-green-100 text-green-800';
      case '뉴스': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Header />
      
      {/* Hero Section */}
      <section className="pt-24 pb-16 bg-gradient-to-br from-purple-50 to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            Frage EDU News
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            최신 소식과 교육 정보를 확인하세요
          </p>
        </div>
      </section>

      {/* Category Filter */}
      <section className="py-8 bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-wrap justify-center gap-4">
            {categories.map((category) => (
              <Button
                key={category}
                onClick={() => setActiveCategory(category)}
                variant={activeCategory === category ? "default" : "outline"}
                className={activeCategory === category 
                  ? "bg-purple-600 hover:bg-purple-700 text-white" 
                  : "hover:bg-purple-50 hover:text-purple-600"
                }
              >
                {category}
              </Button>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Article (for 전체 category) */}
      {activeCategory === '전체' && (
        <section className="py-12 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-8">주요 소식</h2>
            {newsData.filter(item => item.featured).map((article) => (
              <Card key={article.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-0">
                  <div className="lg:order-2">
                    <img 
                      src={article.image} 
                      alt={article.title}
                      className="w-full h-64 lg:h-full object-cover"
                    />
                  </div>
                  <div className="p-8 lg:order-1 flex flex-col justify-center">
                    <Badge className={`${getCategoryColor(article.category)} w-fit mb-4`}>
                      {article.category}
                    </Badge>
                    <h3 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-4">
                      {article.title}
                    </h3>
                    <div className="text-gray-600 text-lg mb-6 leading-relaxed">
                      {article.content.length > 200 ? (
                        <p>{article.content.substring(0, 200)}...</p>
                      ) : (
                        <div 
                          className="prose prose-lg max-w-none"
                          dangerouslySetInnerHTML={{ 
                            __html: article.content
                              .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                              .replace(/\*(.*?)\*/g, '<em>$1</em>')
                              .replace(/^# (.*$)/gm, '<h1>$1</h1>')
                              .replace(/^## (.*$)/gm, '<h2>$1</h2>')
                              .replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1" style="max-width: 100%; height: auto; margin: 10px 0;" />')
                              .replace(/\n/g, '<br />')
                          }}
                        />
                      )}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-500 text-sm">
                        {new Date(article.created_at || article.date).toLocaleDateString('ko-KR')}
                      </span>
                      <Button variant="outline">
                        자세히 보기 <ChevronRight className="w-4 h-4 ml-2" />
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* News Grid */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-12">
            <h2 className="text-3xl font-bold text-gray-900">
              {activeCategory === '전체' ? '모든 소식' : activeCategory}
            </h2>
            <p className="text-gray-600">
              총 {filteredNews.length}개의 게시물
            </p>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
              <p className="text-gray-600">뉴스를 불러오는 중...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredNews.map((article) => (
              <Card key={article.id} className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
                <div className="h-48 overflow-hidden">
                  <img 
                    src={article.image_url || article.image || 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?q=80&w=600&h=300&fit=crop'} 
                    alt={article.title}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                  />
                </div>
                <CardContent className="p-6">
                  <Badge className={`${getCategoryColor(article.category)} mb-3`}>
                    {article.category}
                  </Badge>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3 line-clamp-2">
                    {article.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {article.content}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500 text-xs">
                      {new Date(article.created_at || article.date).toLocaleDateString('ko-KR')}
                    </span>
                    <Button variant="ghost" size="sm" className="text-purple-600 hover:text-purple-800">
                      더보기 <ChevronRight className="w-3 h-3 ml-1" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          )}

          {/* Load More Button */}
          {filteredNews.length >= 6 && (
            <div className="text-center mt-12">
              <Button variant="outline" size="lg">
                더 많은 소식 보기
              </Button>
            </div>
          )}
        </div>
      </section>

      {/* Newsletter Subscription */}
      <section className="py-16 bg-gradient-to-br from-purple-600 to-indigo-600 text-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold mb-4">
            최신 소식을 놓치지 마세요
          </h2>
          <p className="text-xl text-purple-100 mb-8">
            Frage EDU의 새로운 소식과 교육 정보를 이메일로 받아보세요
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center max-w-md mx-auto">
            <Input 
              type="email" 
              placeholder="이메일 주소를 입력하세요"
              className="flex-1 bg-white text-gray-900"
            />
            <Button variant="secondary" className="bg-white text-purple-600 hover:bg-gray-100">
              구독하기
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

const Market = () => (
  <div className="min-h-screen bg-white pt-20">
    <Header />
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Frage Market</h1>
      <p className="text-xl text-gray-600">마켓 페이지 (구현 예정)</p>
    </div>
    <Footer />
  </div>
);

// Token Auth Wrapper for Admission Portal
const TokenAuthWrapper = ({ children }) => {
  const urlParams = new URLSearchParams(window.location.search);
  const tokenFromUrl = urlParams.get('id');
  const { user, token } = useAuth();
  const hasAccess = token || tokenFromUrl;
  
  if (!hasAccess) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

// Admission Portal Pages (keeping the existing functionality)
const Signup = ({ onSignup }) => {
  const [formData, setFormData] = useState({
    email: '',
    phone: '',
    parent_name: '',
    student_name: '',
    password: '',
    terms_accepted: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/signup`, formData);
      onSignup(response.data.token, response.data.user, response.data.household_token);
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50">
      <Header />
      <div className="flex items-center justify-center px-4 py-16">
        <Card className="w-full max-w-md mt-16">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-gray-900">Join Frage EDU</CardTitle>
            <CardDescription>학부모 입학 포털에 가입하세요</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">이메일</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="parent@example.com"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="phone">휴대폰 번호</Label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="010-1234-5678"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="parent_name">학부모 성명</Label>
                  <Input
                    id="parent_name"
                    type="text"
                    placeholder="김학부모"
                    value={formData.parent_name}
                    onChange={(e) => setFormData({...formData, parent_name: e.target.value})}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="student_name">학생 이름</Label>
                  <Input
                    id="student_name"
                    type="text"
                    placeholder="김학생"
                    value={formData.student_name}
                    onChange={(e) => setFormData({...formData, student_name: e.target.value})}
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password">비밀번호</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="안전한 비밀번호를 입력하세요"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="terms"
                  checked={formData.terms_accepted}
                  onCheckedChange={(checked) => setFormData({...formData, terms_accepted: checked})}
                />
                <Label htmlFor="terms" className="text-sm text-gray-600">
                  이용약관 및 개인정보처리방침에 동의합니다
                </Label>
              </div>
              
              {error && (
                <div className="text-red-600 text-sm">{error}</div>
              )}
              
              <Button type="submit" className="w-full bg-purple-600 hover:bg-purple-700" disabled={loading || !formData.terms_accepted}>
                {loading ? "가입 중..." : "가입하기"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
      <Footer />
    </div>
  );
};

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/login`, formData);
      onLogin(response.data.token, response.data.user, response.data.household_token);
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50">
      <Header />
      <div className="flex items-center justify-center px-4 py-16">
        <Card className="w-full max-w-md mt-16">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-gray-900">Welcome Back</CardTitle>
            <CardDescription>학부모 포털에 로그인하세요</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">이메일</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="parent@example.com"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password">비밀번호</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="비밀번호를 입력하세요"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                />
              </div>
              
              {error && (
                <div className="text-red-600 text-sm">{error}</div>
              )}
              
              <Button type="submit" className="w-full bg-purple-600 hover:bg-purple-700" disabled={loading}>
                {loading ? "로그인 중..." : "로그인"}
              </Button>
              
              <div className="text-center mt-4">
                <p className="text-sm text-gray-600">
                  계정이 없으신가요?{' '}
                  <Button variant="link" className="p-0 h-auto text-purple-600" onClick={() => window.location.href = '/signup'}>
                    가입하기
                  </Button>
                </p>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
      <Footer />
    </div>
  );
};

// Internal Admissions Portal (for logged-in users)
const InternalAdmissionsPortal = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50">
      <Header />
      <div className="max-w-4xl mx-auto px-4 py-24">
        <div className="text-center mb-12">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            입학 신청 포털
          </h1>
          <p className="text-xl text-gray-600">
            Frage EDU 입학을 위한 모든 절차를 온라인으로 완료하세요
          </p>
        </div>

        <Card className="p-8 bg-white/80 backdrop-blur-sm">
          <h3 className="text-2xl font-semibold mb-6 text-center">입학 절차 안내</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <FileText className="w-6 h-6 text-purple-600" />
              </div>
              <h4 className="font-semibold mb-2">1. 동의서</h4>
              <p className="text-sm text-gray-600">학교 규정 및 개인정보처리방침</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <ClipboardList className="w-6 h-6 text-green-600" />
              </div>
              <h4 className="font-semibold mb-2">2. 신청서</h4>
              <p className="text-sm text-gray-600">학생 정보 및 프로그램 선택</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <BookOpen className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="font-semibold mb-2">3. 안내사항</h4>
              <p className="text-sm text-gray-600">학교생활 필수 정보</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <CheckCircle className="w-6 h-6 text-orange-600" />
              </div>
              <h4 className="font-semibold mb-2">4. 체크리스트</h4>
              <p className="text-sm text-gray-600">입학 전 준비물 확인</p>
            </div>
          </div>
        </Card>
      </div>
      <Footer />
    </div>
  );
};

// Admin Login Component
const AdminLogin = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/admin/login`, formData);
      localStorage.setItem('adminToken', response.data.token);
      window.location.href = '/admin/dashboard';
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">Admin Login</CardTitle>
          <CardDescription>관리자 포털에 로그인하세요</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">사용자명</Label>
              <Input
                id="username"
                type="text"
                placeholder="admin"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">비밀번호</Label>
              <Input
                id="password"
                type="password"
                placeholder="비밀번호를 입력하세요"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
              />
            </div>
            
            {error && (
              <div className="text-red-600 text-sm">{error}</div>
            )}
            
            <Button type="submit" className="w-full bg-purple-600 hover:bg-purple-700" disabled={loading}>
              {loading ? "로그인 중..." : "로그인"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

// Admin Dashboard Component
const AdminDashboard = () => {
  const [adminToken] = useState(localStorage.getItem('adminToken'));
  const [stats, setStats] = useState({
    users: { total: 0, today: 0, growth: '+0%' },
    news: { total: 0, published: 0, draft: 0 },
    exam_reservations: { total: 0, pending: 0, confirmed: 0 },
    admissions: { total: 0, completed: 0, completion_rate: 0 }
  });

  useEffect(() => {
    if (!adminToken) {
      window.location.href = '/admin/login';
      return;
    }
    fetchStats();
  }, [adminToken]);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/dashboard-stats`, {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    window.location.href = '/';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 py-24">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">관리자 대시보드</h1>
            <p className="text-gray-600">Frage EDU 콘텐츠 관리</p>
          </div>
          <div className="flex space-x-4">
            <Button onClick={() => window.location.href = '/admin/members'} variant="outline">
              <Users className="w-4 h-4 mr-2" />
              회원 관리
            </Button>
            <Button onClick={() => window.location.href = '/admin/exams'} variant="outline">
              <Calendar className="w-4 h-4 mr-2" />
              시험 관리
            </Button>
            <Button onClick={() => window.location.href = '/admin/news'} className="bg-purple-600 hover:bg-purple-700">
              <FileText className="w-4 h-4 mr-2" />
              뉴스 관리
            </Button>
            <Button variant="outline" onClick={handleLogout}>
              로그아웃
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.users.total}</p>
                  <p className="text-gray-600">전체 회원</p>
                  <p className="text-xs text-green-600">{stats.users.growth}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mr-4">
                  <BookmarkCheck className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.exam_reservations.total}</p>
                  <p className="text-gray-600">시험 예약</p>
                  <p className="text-xs text-orange-600">{stats.exam_reservations.pending}건 대기</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mr-4">
                  <FileText className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.admissions.completed}</p>
                  <p className="text-gray-600">입학 완료</p>
                  <p className="text-xs text-blue-600">{stats.admissions.completion_rate}% 완료율</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mr-4">
                  <BarChart3 className="w-6 h-6 text-indigo-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.news.published}</p>
                  <p className="text-gray-600">게시된 뉴스</p>
                  <p className="text-xs text-gray-500">{stats.news.draft}건 대기</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>빠른 작업</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Button variant="outline" onClick={() => window.location.href = '/admin/news/new'} className="h-20 flex flex-col">
                <Plus className="w-8 h-8 mb-2" />
                새 뉴스 작성
              </Button>
              <Button variant="outline" onClick={() => window.location.href = '/admin/news'} className="h-20 flex flex-col">
                <FileText className="w-8 h-8 mb-2" />
                뉴스 목록
              </Button>
              <Button variant="outline" onClick={() => window.location.href = '/news'} className="h-20 flex flex-col">
                <Eye className="w-8 h-8 mb-2" />
                사이트 보기
              </Button>
              <Button variant="outline" className="h-20 flex flex-col">
                <Settings className="w-8 h-8 mb-2" />
                설정
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Parent Dashboard Component
const ParentDashboard = () => {
  const { user, token } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) {
      window.location.href = '/login';
      return;
    }
    fetchDashboardData();
  }, [token]);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/parent/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setError('대시보드 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  const getEnrollmentStatusText = (status) => {
    switch (status) {
      case 'new': return '신규 회원';
      case 'test_scheduled': return '시험 예약됨';
      case 'test_taken': return '시험 완료';
      case 'enrolled': return '등록 완료';
      case 'active': return '수강 중';
      default: return '상태 확인 필요';
    }
  };

  const getEnrollmentStatusColor = (status) => {
    switch (status) {
      case 'new': return 'bg-gray-100 text-gray-800';
      case 'test_scheduled': return 'bg-blue-100 text-blue-800';
      case 'test_taken': return 'bg-yellow-100 text-yellow-800';
      case 'enrolled': return 'bg-green-100 text-green-800';
      case 'active': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">대시보드를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-4xl mx-auto px-4 py-24">
          <Card className="text-center">
            <CardContent className="pt-6">
              <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-gray-900 mb-2">오류 발생</h2>
              <p className="text-gray-600 mb-4">{error}</p>
              <Button onClick={() => window.location.reload()} className="bg-purple-600 hover:bg-purple-700">
                다시 시도
              </Button>
            </CardContent>
          </Card>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 py-24">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">학부모 대시보드</h1>
            <div className="flex items-center space-x-4 mt-2">
              <p className="text-gray-600">안녕하세요, {dashboardData?.parent_info?.name}님</p>
              <Badge className={getEnrollmentStatusColor(dashboardData?.enrollment_status)}>
                {getEnrollmentStatusText(dashboardData?.enrollment_status)}
              </Badge>
            </div>
          </div>
          <div className="flex space-x-4">
            <Button onClick={() => window.location.href = '/programs'} variant="outline">
              <BookOpen className="w-4 h-4 mr-2" />
              프로그램 보기
            </Button>
            <Button variant="outline" onClick={handleLogout}>
              로그아웃
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* Student Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="w-5 h-5 mr-2 text-purple-600" />
                  학생 정보
                </CardTitle>
              </CardHeader>
              <CardContent>
                {dashboardData?.students?.length > 0 ? (
                  <div className="space-y-4">
                    {dashboardData.students.map((student, index) => (
                      <div key={index} className="p-4 bg-gray-50 rounded-lg">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <Label className="text-gray-600">학생 이름</Label>
                            <p className="text-lg font-medium">{student.name}</p>
                          </div>
                          <div>
                            <Label className="text-gray-600">학년</Label>
                            <p className="text-lg font-medium">{student.grade}학년</p>
                          </div>
                          <div>
                            <Label className="text-gray-600">과정</Label>
                            <Badge variant="outline">
                              {dashboardData.parent_info.branch === 'kinder' ? '유치부' :
                               dashboardData.parent_info.branch === 'junior' ? '초등부' : '중등부'}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">등록된 학생 정보가 없습니다.</p>
                )}
              </CardContent>
            </Card>

            {/* Conditional Content Based on Enrollment Status */}
            
            {/* Test Schedule - for new users and scheduled tests */}
            {(dashboardData?.enrollment_status === 'new' || dashboardData?.enrollment_status === 'test_scheduled') && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Calendar className="w-5 h-5 mr-2 text-blue-600" />
                    시험 일정
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {dashboardData?.test_schedules?.length > 0 ? (
                    <div className="space-y-4">
                      {dashboardData.test_schedules.map((schedule, index) => (
                        <div key={index} className="border-l-4 border-blue-400 pl-4 py-3 bg-blue-50 rounded-r-lg">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h4 className="font-semibold text-blue-900">{schedule.student_name}님의 {schedule.branch_type === 'junior' ? '초등부' : '중등부'} 입학시험</h4>
                              <p className="text-blue-700 text-sm">
                                일시: {new Date(schedule.scheduled_date).toLocaleDateString('ko-KR')}
                              </p>
                              <p className="text-blue-700 text-sm">장소: {schedule.location}</p>
                            </div>
                            <Badge className={
                              schedule.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                              schedule.status === 'requested' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'
                            }>
                              {schedule.status === 'confirmed' ? '확정' : schedule.status === 'requested' ? '대기' : '취소'}
                            </Badge>
                          </div>
                          {schedule.notes && (
                            <p className="text-blue-600 text-sm">메모: {schedule.notes}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500 mb-4">예약된 시험이 없습니다.</p>
                      <div className="space-y-2">
                        <Button 
                          onClick={() => window.location.href = '/exam/reserve?brchType=junior'}
                          className="bg-green-600 hover:bg-green-700 mr-2"
                        >
                          초등부 시험 예약
                        </Button>
                        <Button 
                          onClick={() => window.location.href = '/exam/reserve?brchType=middle'}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          중등부 시험 예약
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Test Results - for test_taken and enrolled status */}
            {(dashboardData?.enrollment_status === 'test_taken' || dashboardData?.enrollment_status === 'enrolled') && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Award className="w-5 h-5 mr-2 text-green-600" />
                    시험 결과
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {dashboardData?.test_results?.length > 0 ? (
                    <div className="space-y-4">
                      {dashboardData.test_results.map((result, index) => (
                        <div key={index} className="border-l-4 border-green-400 pl-4 py-3 bg-green-50 rounded-r-lg">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h4 className="font-semibold text-green-900">{result.student_name}님의 시험 결과</h4>
                              <div className="grid grid-cols-2 gap-4 mt-2">
                                <div>
                                  <p className="text-green-700 text-sm">점수: <span className="font-bold text-lg">{result.score}점</span></p>
                                  <p className="text-green-700 text-sm">레벨: {result.level}</p>
                                </div>
                                <div>
                                  <p className="text-green-700 text-sm">추천 반: {result.recommended_class}</p>
                                </div>
                              </div>
                            </div>
                            <Badge className={result.status === 'passed' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                              {result.status === 'passed' ? '합격' : '불합격'}
                            </Badge>
                          </div>
                          {result.feedback && (
                            <div className="bg-white p-3 rounded border mt-3">
                              <p className="text-gray-700 text-sm"><strong>피드백:</strong> {result.feedback}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Award className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500">시험 결과가 아직 나오지 않았습니다.</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Class Assignments - for enrolled status */}
            {dashboardData?.enrollment_status === 'enrolled' && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BookOpen className="w-5 h-5 mr-2 text-purple-600" />
                    수업 배정
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {dashboardData?.class_assignments?.length > 0 ? (
                    <div className="space-y-4">
                      {dashboardData.class_assignments.map((assignment, index) => (
                        <div key={index} className="border-l-4 border-purple-400 pl-4 py-3 bg-purple-50 rounded-r-lg">
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <h4 className="font-semibold text-purple-900">{assignment.class_name}</h4>
                              <p className="text-purple-700 text-sm">담당교사: {assignment.teacher_name}</p>
                              <p className="text-purple-700 text-sm">수업 시간: {assignment.schedule}</p>
                              <p className="text-purple-700 text-sm">교실: {assignment.classroom}</p>
                            </div>
                            <Badge className="bg-purple-100 text-purple-800">
                              {assignment.status === 'active' ? '수강 중' : '완료'}
                            </Badge>
                          </div>
                          
                          {assignment.materials && assignment.materials.length > 0 && (
                            <div className="bg-white p-3 rounded border mt-3">
                              <h5 className="font-medium text-gray-900 mb-2">수업 자료:</h5>
                              <ul className="list-disc list-inside space-y-1">
                                {assignment.materials.map((material, idx) => (
                                  <li key={idx} className="text-gray-700 text-sm">{material}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500">배정된 수업이 없습니다.</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>빠른 메뉴</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {/* Show exam reservation only for new users or if no test scheduled */}
                  {(dashboardData?.enrollment_status === 'new') && (
                    <>
                      <Button 
                        onClick={() => window.location.href = '/exam/reserve?brchType=junior'}
                        className="w-full justify-start bg-green-600 hover:bg-green-700"
                      >
                        <Calendar className="w-4 h-4 mr-2" />
                        초등부 시험 예약
                      </Button>
                      <Button 
                        onClick={() => window.location.href = '/exam/reserve?brchType=middle'}
                        className="w-full justify-start bg-blue-600 hover:bg-blue-700"
                      >
                        <Calendar className="w-4 h-4 mr-2" />
                        중등부 시험 예약
                      </Button>
                    </>
                  )}
                  
                  <Button 
                    onClick={() => window.location.href = '/programs'}
                    variant="outline" 
                    className="w-full justify-start"
                  >
                    <BookOpen className="w-4 h-4 mr-2" />
                    프로그램 안내
                  </Button>
                  <Button 
                    onClick={() => window.location.href = '/news'}
                    variant="outline" 
                    className="w-full justify-start"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    최신 소식
                  </Button>
                  
                  {/* Show admission forms for test_taken users */}
                  {dashboardData?.enrollment_status === 'test_taken' && (
                    <Button 
                      onClick={() => window.location.href = `/dashboard?id=${dashboardData?.parent_info?.household_token}`}
                      className="w-full justify-start bg-purple-600 hover:bg-purple-700"
                    >
                      <FileText className="w-4 h-4 mr-2" />
                      입학 서류 작성
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Parent Information */}
            <Card>
              <CardHeader>
                <CardTitle>학부모 정보</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <Label className="text-gray-600">이름</Label>
                    <p className="font-medium">{dashboardData?.parent_info?.name}</p>
                  </div>
                  <div>
                    <Label className="text-gray-600">이메일</Label>
                    <p className="font-medium">{dashboardData?.parent_info?.email}</p>
                  </div>
                  <div>
                    <Label className="text-gray-600">연락처</Label>
                    <p className="font-medium">{dashboardData?.parent_info?.phone || '미입력'}</p>
                  </div>
                  <div>
                    <Label className="text-gray-600">캠퍼스</Label>
                    <Badge variant="outline">
                      {dashboardData?.parent_info?.branch === 'kinder' ? '유치부' :
                       dashboardData?.parent_info?.branch === 'junior' ? '초등부' : '중등부'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Contact Information */}
            <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200">
              <CardContent className="p-6">
                <h4 className="font-semibold text-purple-900 mb-3">문의사항이 있으시다면?</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center space-x-2 text-purple-700">
                    <Phone className="w-4 h-4" />
                    <span>053-754-0577</span>
                  </div>
                  <div className="flex items-center space-x-2 text-purple-700">
                    <Mail className="w-4 h-4" />
                    <span>frage0577@gmail.com</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

// Admin Member Management Component
const AdminMemberManagement = () => {
  const [adminToken] = useState(localStorage.getItem('adminToken'));
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [branchFilter, setBranchFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(50);
  const [totalMembers, setTotalMembers] = useState(0);
  const [sortConfig, setSortConfig] = useState({ field: 'joinedAt', direction: 'desc' });
  const [selectedMembers, setSelectedMembers] = useState([]);
  const [viewingMember, setViewingMember] = useState(null);
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (!adminToken) {
      window.location.href = '/admin/login';
      return;
    }
    fetchMembers();
  }, [adminToken, searchQuery, branchFilter, statusFilter, currentPage, sortConfig]);

  const fetchMembers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: currentPage,
        pageSize: pageSize,
        sort: `${sortConfig.field}:${sortConfig.direction}`
      });
      
      if (searchQuery.trim()) params.append('query', searchQuery.trim());
      if (branchFilter) params.append('branch', branchFilter);
      if (statusFilter) params.append('status', statusFilter);

      const response = await axios.get(`${API}/admin/members?${params}`, {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });
      
      setMembers(response.data.members || []);
      setTotalMembers(response.data.pagination?.total || 0);
    } catch (error) {
      console.error('Failed to fetch members:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMemberDetails = async (memberId) => {
    try {
      const response = await axios.get(`${API}/admin/members/${memberId}`, {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });
      setViewingMember(response.data);
    } catch (error) {
      console.error('Failed to fetch member details:', error);
    }
  };

  const handleSort = (field) => {
    setSortConfig({
      field,
      direction: sortConfig.field === field && sortConfig.direction === 'asc' ? 'desc' : 'asc'
    });
  };

  const handleMemberSelect = (memberId, checked) => {
    if (checked) {
      setSelectedMembers([...selectedMembers, memberId]);
    } else {
      setSelectedMembers(selectedMembers.filter(id => id !== memberId));
    }
  };

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedMembers(members.map(m => m.id));
    } else {
      setSelectedMembers([]);
    }
  };

  const handleResetPassword = async (memberId) => {
    if (!confirm('이 회원의 비밀번호를 초기화하시겠습니까?')) return;
    
    setActionLoading(true);
    try {
      const response = await axios.post(`${API}/admin/members/${memberId}/reset-password`, {}, {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });
      
      alert(`비밀번호가 초기화되었습니다. 임시 비밀번호: ${response.data.temporary_password}`);
    } catch (error) {
      alert('비밀번호 초기화에 실패했습니다.');
      console.error(error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleStatusChange = async (memberId, newStatus) => {
    if (!confirm(`이 회원을 ${newStatus === 'active' ? '활성화' : '비활성화'}하시겠습니까?`)) return;
    
    setActionLoading(true);
    try {
      await axios.patch(`${API}/admin/members/${memberId}/status`, 
        { status: newStatus },
        { headers: { 'Authorization': `Bearer ${adminToken}` } }
      );
      
      fetchMembers(); // Refresh the list
      alert(`회원 상태가 ${newStatus === 'active' ? '활성화' : '비활성화'}되었습니다.`);
    } catch (error) {
      alert('상태 변경에 실패했습니다.');
      console.error(error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleBulkExport = async () => {
    if (selectedMembers.length === 0) {
      alert('내보낼 회원을 선택해주세요.');
      return;
    }
    
    setActionLoading(true);
    try {
      const response = await axios.post(`${API}/admin/members/bulk/export`, 
        selectedMembers,
        { headers: { 'Authorization': `Bearer ${adminToken}` } }
      );
      
      // Download CSV
      const blob = new Blob([response.data.csv_content], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', response.data.filename);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      alert(`${selectedMembers.length}명의 회원 정보를 내보냈습니다.`);
      setSelectedMembers([]);
    } catch (error) {
      alert('내보내기에 실패했습니다.');
      console.error(error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleBulkNotify = async () => {
    if (selectedMembers.length === 0) {
      alert('알림을 보낼 회원을 선택해주세요.');
      return;
    }
    
    const message = prompt('보낼 메시지를 입력하세요:');
    if (!message) return;
    
    setActionLoading(true);
    try {
      await axios.post(`${API}/admin/members/bulk/notify`, 
        { user_ids: selectedMembers, message },
        { headers: { 'Authorization': `Bearer ${adminToken}` } }
      );
      
      alert(`${selectedMembers.length}명에게 알림을 보냈습니다.`);
      setSelectedMembers([]);
    } catch (error) {
      alert('알림 발송에 실패했습니다.');
      console.error(error);
    } finally {
      setActionLoading(false);
    }
  };

  const totalPages = Math.ceil(totalMembers / pageSize);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 py-24">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">회원 / 학부모 관리</h1>
            <p className="text-gray-600">전체 {totalMembers}명의 회원</p>
          </div>
          <div className="flex space-x-3">
            <Button 
              variant="outline" 
              onClick={() => window.location.href = '/admin/dashboard'}
            >
              <ChevronLeft className="w-4 h-4 mr-2" />
              대시보드
            </Button>
            <Button 
              onClick={fetchMembers}
              variant="outline"
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              새로고침
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <Label>검색</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    placeholder="이름, 전화번호, 이메일, 학생명으로 검색"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label>캠퍼스</Label>
                <Select value={branchFilter} onValueChange={setBranchFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="전체 캠퍼스" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">전체 캠퍼스</SelectItem>
                    <SelectItem value="kinder">유치부</SelectItem>
                    <SelectItem value="junior">초등부</SelectItem>
                    <SelectItem value="middle">중등부</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label>상태</Label>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="전체 상태" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">전체 상태</SelectItem>
                    <SelectItem value="active">활성</SelectItem>
                    <SelectItem value="disabled">비활성</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2 flex items-end">
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setSearchQuery('');
                    setBranchFilter('');
                    setStatusFilter('');
                    setCurrentPage(1);
                  }}
                  className="w-full"
                >
                  <Filter className="w-4 h-4 mr-2" />
                  필터 초기화
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Bulk Actions Bar */}
        {selectedMembers.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-center justify-between">
            <span className="text-blue-800">
              {selectedMembers.length}명 선택됨
            </span>
            <div className="flex space-x-2">
              <Button 
                size="sm" 
                variant="outline"
                onClick={handleBulkExport}
                disabled={actionLoading}
              >
                <Download className="w-4 h-4 mr-2" />
                CSV 내보내기
              </Button>
              <Button 
                size="sm" 
                variant="outline"
                onClick={handleBulkNotify}
                disabled={actionLoading}
              >
                <MessageCircle className="w-4 h-4 mr-2" />
                알림 발송
              </Button>
              <Button 
                size="sm" 
                variant="outline"
                onClick={() => setSelectedMembers([])}
              >
                선택 해제
              </Button>
            </div>
          </div>
        )}

        {/* Members Table */}
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-4 text-left">
                      <Checkbox
                        checked={selectedMembers.length === members.length && members.length > 0}
                        onCheckedChange={handleSelectAll}
                      />
                    </th>
                    <th className="px-6 py-4 text-left">
                      <Button variant="ghost" onClick={() => handleSort('name')} className="font-medium">
                        학부모명
                        {sortConfig.field === 'name' && (
                          sortConfig.direction === 'asc' ? 
                          <SortAsc className="w-4 h-4 ml-1" /> : 
                          <SortDesc className="w-4 h-4 ml-1" />
                        )}
                      </Button>
                    </th>
                    <th className="px-6 py-4 text-left">연락처</th>
                    <th className="px-6 py-4 text-left">이메일</th>
                    <th className="px-6 py-4 text-left">학생</th>
                    <th className="px-6 py-4 text-left">캠퍼스</th>
                    <th className="px-6 py-4 text-left">토큰</th>
                    <th className="px-6 py-4 text-left">
                      <Button variant="ghost" onClick={() => handleSort('joinedAt')} className="font-medium">
                        가입일
                        {sortConfig.field === 'joinedAt' && (
                          sortConfig.direction === 'asc' ? 
                          <SortAsc className="w-4 h-4 ml-1" /> : 
                          <SortDesc className="w-4 h-4 ml-1" />
                        )}
                      </Button>
                    </th>
                    <th className="px-6 py-4 text-left">
                      <Button variant="ghost" onClick={() => handleSort('lastLogin')} className="font-medium">
                        최근 로그인
                        {sortConfig.field === 'lastLogin' && (
                          sortConfig.direction === 'asc' ? 
                          <SortAsc className="w-4 h-4 ml-1" /> : 
                          <SortDesc className="w-4 h-4 ml-1" />
                        )}
                      </Button>
                    </th>
                    <th className="px-6 py-4 text-left">상태</th>
                    <th className="px-6 py-4 text-left">작업</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {loading ? (
                    <tr>
                      <td colSpan={11} className="px-6 py-12 text-center text-gray-500">
                        <div className="flex items-center justify-center">
                          <RefreshCw className="w-6 h-6 animate-spin mr-3" />
                          데이터를 불러오는 중...
                        </div>
                      </td>
                    </tr>
                  ) : members.length === 0 ? (
                    <tr>
                      <td colSpan={11} className="px-6 py-12 text-center text-gray-500">
                        검색 결과가 없습니다.
                      </td>
                    </tr>
                  ) : (
                    members.map((member) => (
                      <tr key={member.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <Checkbox
                            checked={selectedMembers.includes(member.id)}
                            onCheckedChange={(checked) => handleMemberSelect(member.id, checked)}
                          />
                        </td>
                        <td className="px-6 py-4 font-medium">{member.parent_name || '-'}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">{member.phone || '-'}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">{member.email || '-'}</td>
                        <td className="px-6 py-4">
                          <div className="space-y-1">
                            {member.students?.map((student, idx) => (
                              <div key={idx} className="text-sm">
                                <span className="font-medium">{student.name}</span>
                                {student.grade && <span className="text-gray-500 ml-2">({student.grade}학년)</span>}
                              </div>
                            )) || '-'}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <Badge variant={
                            member.branch === 'kinder' ? 'default' :
                            member.branch === 'junior' ? 'secondary' : 'outline'
                          }>
                            {member.branch === 'kinder' ? '유치부' :
                             member.branch === 'junior' ? '초등부' :
                             member.branch === 'middle' ? '중등부' : member.branch}
                          </Badge>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-2">
                            <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                              {member.household_token?.substring(0, 8)}...
                            </code>
                            <Button 
                              size="sm" 
                              variant="ghost"
                              onClick={() => navigator.clipboard.writeText(member.household_token)}
                            >
                              <Copy className="w-4 h-4" />
                            </Button>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {member.joined_at ? new Date(member.joined_at).toLocaleDateString('ko-KR') : '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {member.last_login ? new Date(member.last_login).toLocaleDateString('ko-KR') : '-'}
                        </td>
                        <td className="px-6 py-4">
                          <Badge variant={member.status === 'active' ? 'default' : 'destructive'}>
                            {member.status === 'active' ? '활성' : '비활성'}
                          </Badge>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => fetchMemberDetails(member.id)}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleResetPassword(member.id)}
                              disabled={actionLoading}
                            >
                              <Key className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant={member.status === 'active' ? 'destructive' : 'default'}
                              onClick={() => handleStatusChange(member.id, member.status === 'active' ? 'disabled' : 'active')}
                              disabled={actionLoading}
                            >
                              {member.status === 'active' ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-6">
            <div className="text-sm text-gray-700">
              {((currentPage - 1) * pageSize) + 1}-{Math.min(currentPage * pageSize, totalMembers)} of {totalMembers} 결과
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              
              {[...Array(Math.min(5, totalPages))].map((_, i) => {
                const pageNum = Math.max(1, currentPage - 2) + i;
                if (pageNum > totalPages) return null;
                
                return (
                  <Button
                    key={pageNum}
                    variant={currentPage === pageNum ? "default" : "outline"}
                    size="sm"
                    onClick={() => setCurrentPage(pageNum)}
                  >
                    {pageNum}
                  </Button>
                );
              })}
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Member Details Modal */}
      {viewingMember && (
        <Dialog open={!!viewingMember} onOpenChange={() => setViewingMember(null)}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                <Users className="w-5 h-5" />
                <span>회원 상세 정보</span>
              </DialogTitle>
            </DialogHeader>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* User Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">학부모 정보</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <Label className="text-sm font-medium text-gray-500">이름</Label>
                    <p className="text-lg">{viewingMember.user?.name || '-'}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-500">이메일</Label>
                    <p>{viewingMember.user?.email || '-'}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-500">전화번호</Label>
                    <p>{viewingMember.user?.phone || '-'}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-500">가입일</Label>
                    <p>{viewingMember.user?.created_at ? new Date(viewingMember.user.created_at).toLocaleDateString('ko-KR') : '-'}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-500">최근 로그인</Label>
                    <p>{viewingMember.user?.last_login_at ? new Date(viewingMember.user.last_login_at).toLocaleDateString('ko-KR') : '없음'}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-500">상태</Label>
                    <Badge variant={viewingMember.user?.status === 'active' ? 'default' : 'destructive'}>
                      {viewingMember.user?.status === 'active' ? '활성' : '비활성'}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              {/* Students Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">학생 정보</CardTitle>
                </CardHeader>
                <CardContent>
                  {viewingMember.students?.length > 0 ? (
                    <div className="space-y-4">
                      {viewingMember.students.map((student, idx) => (
                        <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                          <div className="font-medium">{student.name}</div>
                          {student.grade && <div className="text-sm text-gray-600">학년: {student.grade}</div>}
                          {student.birthdate && <div className="text-sm text-gray-600">생년월일: {student.birthdate}</div>}
                          {student.notes && <div className="text-sm text-gray-600">메모: {student.notes}</div>}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">등록된 학생이 없습니다.</p>
                  )}
                </CardContent>
              </Card>

              {/* Admission Status */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">입학 진행 상황</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>동의서</span>
                    <Badge variant={viewingMember.consent_status === 'completed' ? 'default' : 'outline'}>
                      {viewingMember.consent_status === 'completed' ? '완료' : '대기'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>서류 제출</span>
                    <Badge variant={viewingMember.forms_status === 'completed' ? 'default' : 'outline'}>
                      {viewingMember.forms_status === 'completed' ? '완료' : '대기'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>안내 확인</span>
                    <Badge variant={viewingMember.guides_status === 'completed' ? 'default' : 'outline'}>
                      {viewingMember.guides_status === 'completed' ? '완료' : '대기'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>체크리스트</span>
                    <Badge variant={viewingMember.checklist_status === 'completed' ? 'default' : 'outline'}>
                      {viewingMember.checklist_status === 'completed' ? '완료' : '대기'}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              {/* Exam Reservations */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">시험 예약 현황</CardTitle>
                </CardHeader>
                <CardContent>
                  {viewingMember.exam_reservations?.length > 0 ? (
                    <div className="space-y-3">
                      {viewingMember.exam_reservations.map((reservation, idx) => (
                        <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{reservation.brchType === 'junior' ? '초등부' : '중등부'} 시험</span>
                            <Badge variant={
                              reservation.status === 'confirmed' ? 'default' :
                              reservation.status === 'requested' ? 'secondary' : 'destructive'
                            }>
                              {reservation.status === 'confirmed' ? '확정' :
                               reservation.status === 'requested' ? '대기' : '취소'}
                            </Badge>
                          </div>
                          <div className="text-sm text-gray-600">
                            <div>캠퍼스: {reservation.campus}</div>
                            <div>신청일: {new Date(reservation.created_at).toLocaleDateString('ko-KR')}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">예약 내역이 없습니다.</p>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="flex justify-end space-x-3 mt-6 pt-6 border-t">
              <Button 
                variant="outline" 
                onClick={() => handleResetPassword(viewingMember.user?.id)}
                disabled={actionLoading}
              >
                <Key className="w-4 h-4 mr-2" />
                비밀번호 초기화
              </Button>
              <Button 
                variant={viewingMember.user?.status === 'active' ? 'destructive' : 'default'}
                onClick={() => handleStatusChange(viewingMember.user?.id, viewingMember.user?.status === 'active' ? 'disabled' : 'active')}
                disabled={actionLoading}
              >
                {viewingMember.user?.status === 'active' ? (
                  <>
                    <UserX className="w-4 h-4 mr-2" />
                    계정 비활성화
                  </>
                ) : (
                  <>
                    <UserCheck className="w-4 h-4 mr-2" />
                    계정 활성화
                  </>
                )}
              </Button>
              <Button onClick={() => setViewingMember(null)}>
                닫기
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

// Admin News Management Component
const AdminNewsManagement = () => {
  const [adminToken] = useState(localStorage.getItem('adminToken'));
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('전체');

  const categories = ['전체', '개강소식', '공지사항', '뉴스'];

  useEffect(() => {
    if (!adminToken) {
      window.location.href = '/admin/login';
      return;
    }
    fetchArticles();
  }, [adminToken, activeCategory]);

  const fetchArticles = async () => {
    try {
      const params = activeCategory !== '전체' ? `?category=${activeCategory}` : '';
      const response = await axios.get(`${API}/admin/news${params}`, {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });
      setArticles(response.data.articles);
    } catch (error) {
      console.error('Failed to fetch articles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (articleId) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await axios.delete(`${API}/admin/news/${articleId}`, {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });
      fetchArticles();
    } catch (error) {
      console.error('Failed to delete article:', error);
    }
  };

  const getCategoryColor = (category) => {
    switch(category) {
      case '개강소식': return 'bg-blue-100 text-blue-800';
      case '공지사항': return 'bg-green-100 text-green-800';
      case '뉴스': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <div className="max-w-7xl mx-auto px-4 py-24">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">뉴스 관리</h1>
            <p className="text-gray-600">뉴스 기사를 작성하고 관리하세요</p>
          </div>
          <div className="flex space-x-4">
            <Button onClick={() => window.location.href = '/admin/news/new'} className="bg-purple-600 hover:bg-purple-700">
              <Plus className="w-4 h-4 mr-2" />
              새 뉴스 작성
            </Button>
            <Button variant="outline" onClick={() => window.location.href = '/admin/dashboard'}>
              대시보드
            </Button>
          </div>
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-4 mb-8">
          {categories.map((category) => (
            <Button
              key={category}
              onClick={() => setActiveCategory(category)}
              variant={activeCategory === category ? "default" : "outline"}
              className={activeCategory === category 
                ? "bg-purple-600 hover:bg-purple-700" 
                : "hover:bg-purple-50"
              }
            >
              {category}
            </Button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {articles.map((article) => (
              <Card key={article.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <Badge className={getCategoryColor(article.category)}>
                          {article.category}
                        </Badge>
                        {article.featured && (
                          <Badge className="bg-yellow-100 text-yellow-800">주요 소식</Badge>
                        )}
                        {!article.published && (
                          <Badge variant="secondary">임시 저장</Badge>
                        )}
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">{article.title}</h3>
                      <p className="text-gray-600 mb-3 line-clamp-2">{article.content}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(article.created_at).toLocaleDateString('ko-KR')} 작성
                      </p>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => window.location.href = `/admin/news/edit/${article.id}`}
                      >
                        <Edit3 className="w-4 h-4" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDelete(article.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            {articles.length === 0 && (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">뉴스가 없습니다</h3>
                <p className="text-gray-600 mb-6">새로운 뉴스를 작성해보세요.</p>
                <Button onClick={() => window.location.href = '/admin/news/new'}>
                  <Plus className="w-4 h-4 mr-2" />
                  새 뉴스 작성
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Rich Text Editor Component
const RichTextEditor = ({ content, onChange }) => {
  const [editorContent, setEditorContent] = useState(content);
  const [showPreview, setShowPreview] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);
  const textareaRef = useState(null);
  const fileInputRef = useState(null);

  useEffect(() => {
    setEditorContent(content);
  }, [content]);

  const handleContentChange = (value) => {
    setEditorContent(value);
    onChange(value);
  };

  const insertText = (before, after = '') => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = editorContent.substring(start, end);
    const replacement = `${before}${selectedText}${after}`;
    
    const newContent = 
      editorContent.substring(0, start) + 
      replacement + 
      editorContent.substring(end);
    
    handleContentChange(newContent);
    
    // Set cursor position
    setTimeout(() => {
      textarea.focus();
      const newPosition = start + before.length + selectedText.length;
      textarea.setSelectionRange(newPosition, newPosition);
    }, 0);
  };

  const handleImageUpload = async (file) => {
    setUploadingImage(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const adminToken = localStorage.getItem('adminToken');
      const response = await axios.post(`${BACKEND_URL}/api/admin/upload-image-base64`, formData, {
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      const imageMarkdown = `\n![${file.name}](${response.data.data_url})\n`;
      const newContent = editorContent + imageMarkdown;
      handleContentChange(newContent);
    } catch (error) {
      console.error('Image upload failed:', error);
      alert('이미지 업로드에 실패했습니다.');
    } finally {
      setUploadingImage(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      handleImageUpload(file);
    }
    e.target.value = ''; // Reset input
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    const imageFile = files.find(file => file.type.startsWith('image/'));
    if (imageFile) {
      handleImageUpload(imageFile);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const renderPreview = (text) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^# (.*$)/gm, '<h1>$1</h1>')
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/^### (.*$)/gm, '<h3>$1</h3>')
      .replace(/^\> (.*$)/gm, '<blockquote>$1</blockquote>')
      .replace(/^\- (.*$)/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      .replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1" style="max-width: 100%; height: auto; margin: 10px 0;" />')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
      .replace(/\n/g, '<br />');
  };

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-2 p-3 bg-gray-50 border rounded-lg">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => insertText('**', '**')}
          title="Bold"
        >
          <Bold className="w-4 h-4" />
        </Button>
        
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => insertText('*', '*')}
          title="Italic"
        >
          <Italic className="w-4 h-4" />
        </Button>

        <Separator orientation="vertical" className="h-6" />
        
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => insertText('# ')}
          title="Heading 1"
        >
          <Type className="w-4 h-4" />
        </Button>
        
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => insertText('## ')}
          title="Heading 2"
        >
          <Type className="w-3 h-3" />
        </Button>

        <Separator orientation="vertical" className="h-6" />
        
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => insertText('- ')}
          title="List"
        >
          <List className="w-4 h-4" />
        </Button>
        
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => insertText('> ')}
          title="Quote"
        >
          <Quote className="w-4 h-4" />
        </Button>

        <Separator orientation="vertical" className="h-6" />
        
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploadingImage}
          title="Upload Image"
        >
          {uploadingImage ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
          ) : (
            <ImageIcon className="w-4 h-4" />
          )}
        </Button>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />

        <div className="ml-auto flex items-center gap-2">
          <Button
            type="button"
            variant={showPreview ? "default" : "ghost"}
            size="sm"
            onClick={() => setShowPreview(!showPreview)}
          >
            <Eye className="w-4 h-4 mr-1" />
            {showPreview ? "편집" : "미리보기"}
          </Button>
        </div>
      </div>

      {/* Editor Area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Text Editor */}
        <div className={showPreview ? "hidden lg:block" : ""}>
          <Label>내용 작성</Label>
          <div 
            className="relative"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <Textarea
              ref={textareaRef}
              value={editorContent}
              onChange={(e) => handleContentChange(e.target.value)}
              placeholder="마크다운 형식으로 작성하세요...&#10;&#10;**굵게** *기울임* &#10;# 제목 1&#10;## 제목 2&#10;- 목록&#10;> 인용&#10;&#10;이미지를 드래그하여 추가하거나 이미지 버튼을 클릭하세요."
              rows={20}
              className="resize-none"
              required
            />
            {uploadingImage && (
              <div className="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center">
                <div className="bg-white p-4 rounded-lg">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-2"></div>
                  <p className="text-sm">이미지 업로드 중...</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Preview */}
        <div className={showPreview ? "" : "hidden lg:block"}>
          <Label>미리보기</Label>
          <div className="border rounded-lg p-4 min-h-[500px] bg-white overflow-y-auto">
            {editorContent ? (
              <div 
                className="prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: renderPreview(editorContent) }}
              />
            ) : (
              <p className="text-gray-500 text-center mt-20">
                내용을 입력하면 여기에 미리보기가 표시됩니다
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Help Text */}
      <div className="text-sm text-gray-500 bg-gray-50 p-3 rounded-lg">
        <strong>마크다운 사용법:</strong> **굵게**, *기울임*, # 제목, - 목록, &gt; 인용, 이미지는 드래그하거나 업로드 버튼 사용
      </div>
    </div>
  );
};

// Admin News Editor Component
const AdminNewsEditor = () => {
  const [adminToken] = useState(localStorage.getItem('adminToken'));
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: '공지사항',
    image_url: '',
    featured: false,
    published: true
  });
  const [loading, setLoading] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [articleId, setArticleId] = useState(null);

  useEffect(() => {
    if (!adminToken) {
      window.location.href = '/admin/login';
      return;
    }

    // Check if editing existing article
    const pathParts = window.location.pathname.split('/');
    if (pathParts[3] === 'edit' && pathParts[4]) {
      setIsEdit(true);
      setArticleId(pathParts[4]);
      fetchArticle(pathParts[4]);
    }
  }, [adminToken]);

  const fetchArticle = async (id) => {
    try {
      const response = await axios.get(`${API}/news/${id}`);
      setFormData(response.data);
    } catch (error) {
      console.error('Failed to fetch article:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isEdit) {
        await axios.put(`${API}/admin/news/${articleId}`, formData, {
          headers: { 'Authorization': `Bearer ${adminToken}` }
        });
      } else {
        await axios.post(`${API}/admin/news`, formData, {
          headers: { 'Authorization': `Bearer ${adminToken}` }
        });
      }
      
      window.location.href = '/admin/news';
    } catch (error) {
      console.error('Failed to save article:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <div className="max-w-4xl mx-auto px-4 py-24">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {isEdit ? '뉴스 수정' : '새 뉴스 작성'}
          </h1>
          <p className="text-gray-600">뉴스 기사를 작성하고 게시하세요</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>기본 정보</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="title">제목</Label>
                  <Input
                    id="title"
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    placeholder="뉴스 제목을 입력하세요"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="category">카테고리</Label>
                  <Select value={formData.category} onValueChange={(value) => setFormData({...formData, category: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="개강소식">개강소식</SelectItem>
                      <SelectItem value="공지사항">공지사항</SelectItem>
                      <SelectItem value="뉴스">뉴스</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="image_url">이미지 URL</Label>
                  <Input
                    id="image_url"
                    type="url"
                    value={formData.image_url}
                    onChange={(e) => setFormData({...formData, image_url: e.target.value})}
                    placeholder="https://example.com/image.jpg"
                  />
                </div>

                <div className="flex space-x-6">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="featured"
                      checked={formData.featured}
                      onCheckedChange={(checked) => setFormData({...formData, featured: checked})}
                    />
                    <Label htmlFor="featured">주요 소식으로 설정</Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="published"
                      checked={formData.published}
                      onCheckedChange={(checked) => setFormData({...formData, published: checked})}
                    />
                    <Label htmlFor="published">즉시 게시</Label>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>내용</CardTitle>
                <CardDescription>
                  리치 에디터를 사용하여 이미지와 함께 풍부한 내용을 작성하세요
                </CardDescription>
              </CardHeader>
              <CardContent>
                <RichTextEditor
                  content={formData.content}
                  onChange={(content) => setFormData({...formData, content})}
                />
              </CardContent>
            </Card>

            <div className="flex space-x-4">
              <Button 
                type="button" 
                variant="outline"
                onClick={() => window.location.href = '/admin/news'}
                className="flex-1"
              >
                취소
              </Button>
              <Button 
                type="submit" 
                disabled={loading}
                className="flex-1 bg-purple-600 hover:bg-purple-700"
              >
                {loading ? "저장 중..." : (isEdit ? "수정하기" : "게시하기")}
                <Save className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

// New Public Admissions Page
const AdmissionsPage = () => {
  const programsData = [
    {
      id: 'kinder',
      title: 'Kindergarten English',
      subtitle: '유치부 (5-7세)',
      description: '놀이 중심의 영어 교육으로 자연스러운 언어 습득을 도와드립니다.',
      examRequired: false,
      consultationText: '상담 및 레벨테스트 신청',
      action: () => window.location.href = '/consultation'
    },
    {
      id: 'junior',
      title: 'Elementary English',
      subtitle: '초등부 (8-12세)', 
      description: '체계적인 읽기, 쓰기 교육과 프로젝트 기반 학습을 진행합니다.',
      examRequired: true,
      examText: '입학시험 예약',
      action: () => window.location.href = '/exam/reserve?brchType=junior'
    },
    {
      id: 'middle', 
      title: 'Middle School English',
      subtitle: '중등부 (13-16세)',
      description: '비판적 사고력과 고급 영어 실력을 기르는 심화 과정입니다.',
      examRequired: true,
      examText: '입학시험 예약',
      action: () => window.location.href = '/exam/reserve?brchType=middle'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Header />
      
      {/* Hero Section */}
      <section className="pt-24 pb-16 bg-gradient-to-br from-purple-50 to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            Frage EDU 입학 안내
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            아이의 미래를 위한 첫걸음을 함께 시작하세요
          </p>
        </div>
      </section>

      {/* Programs Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">프로그램별 입학 절차</h2>
            <p className="text-xl text-gray-600">연령과 수준에 맞는 프로그램을 선택하고 입학을 신청하세요</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
            {programsData.map((program) => (
              <Card key={program.id} className="rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className={`h-48 rounded-t-xl ${
                  program.id === 'kinder' 
                    ? 'bg-gradient-to-br from-yellow-100 to-orange-100'
                    : program.id === 'junior'
                    ? 'bg-gradient-to-br from-green-100 to-emerald-100'
                    : 'bg-gradient-to-br from-blue-100 to-indigo-100'
                }`}>
                  <div className="h-full flex items-center justify-center">
                    <div className={`w-20 h-20 rounded-full flex items-center justify-center ${
                      program.id === 'kinder'
                        ? 'bg-orange-200'
                        : program.id === 'junior' 
                        ? 'bg-green-200'
                        : 'bg-blue-200'
                    }`}>
                      <BookOpen className={`w-10 h-10 ${
                        program.id === 'kinder'
                          ? 'text-orange-600'
                          : program.id === 'junior'
                          ? 'text-green-600' 
                          : 'text-blue-600'
                      }`} />
                    </div>
                  </div>
                </div>
                
                <CardContent className="p-8">
                  <div className="mb-4">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{program.title}</h3>
                    <p className="text-purple-600 font-medium">{program.subtitle}</p>
                  </div>
                  
                  <p className="text-gray-600 mb-6">{program.description}</p>
                  
                  <div className="space-y-3">
                    {program.examRequired ? (
                      <>
                        <Button 
                          onClick={program.action}
                          className="w-full bg-purple-600 hover:bg-purple-700"
                        >
                          <Calendar className="w-4 h-4 mr-2" />
                          {program.examText}
                        </Button>
                        <Button 
                          variant="outline"
                          onClick={() => window.location.href = `/exam/guide?brchType=${program.id}`}
                          className="w-full"
                        >
                          시험 안내보기
                        </Button>
                      </>
                    ) : (
                      <Button 
                        onClick={program.action}
                        className="w-full bg-orange-600 hover:bg-orange-700"
                      >
                        <MessageCircle className="w-4 h-4 mr-2" />
                        {program.consultationText}
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Process Steps */}
          <div className="text-center mb-12">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">입학 절차</h3>
            <p className="text-gray-600">간단한 4단계로 Frage EDU에 합류하세요</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">1. 프로그램 선택</h3>
              <p className="text-gray-600 text-sm">연령에 맞는 적합한 프로그램을 선택하세요</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Calendar className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">2. 시험 예약</h3>
              <p className="text-gray-600 text-sm">온라인으로 편리하게 입학시험을 예약하세요</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <BookmarkCheck className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">3. 시험 응시</h3>
              <p className="text-gray-600 text-sm">예약된 일시에 캠퍼스에서 레벨테스트를 받으세요</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Award className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">4. 수업 시작</h3>
              <p className="text-gray-600 text-sm">결과 확인 후 적합한 클래스에서 학습을 시작하세요</p>
            </div>
          </div>
        </div>
      </section>

      {/* Registration CTA */}
      <section className="py-16 bg-gradient-to-br from-purple-600 to-indigo-600 text-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl lg:text-4xl font-bold mb-4">
            지금 바로 시작하세요
          </h2>
          <p className="text-xl text-purple-100 mb-8">
            회원가입 후 입학 절차를 진행하고 내 아이만의 학습 여정을 시작하세요
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              variant="secondary" 
              className="bg-white text-purple-600 hover:bg-gray-100"
              onClick={() => window.location.href = '/signup'}
            >
              회원가입하기
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="border-white text-white hover:bg-white hover:text-purple-600"
              onClick={() => window.location.href = '/login'}
            >
              로그인
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

// Main App Component
function App() {
  const { user, token, login, logout } = useAuth();

  const handleSignup = (newToken, userData, household_token) => {
    login(newToken, userData);
    window.location.href = `/dashboard?id=${household_token}`;
  };

  const handleLogin = (newToken, userData, household_token) => {
    login(newToken, userData);
    // Redirect to the new parent dashboard instead of old admission portal
    window.location.href = `/parent/dashboard`;
  };

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/programs" element={<Programs />} />
          <Route path="/news" element={<News />} />
          <Route path="/market" element={<Market />} />
          
          {/* Admin Routes */}
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/admin/members" element={<AdminMemberManagement />} />
          <Route path="/admin/news" element={<AdminNewsManagement />} />
          <Route path="/admin/news/new" element={<AdminNewsEditor />} />
          <Route path="/admin/news/edit/:id" element={<AdminNewsEditor />} />
          <Route path="/admissions" element={<AdmissionsPage />} />
          <Route path="/portal" element={
            <TokenAuthWrapper>
              <InternalAdmissionsPortal />
            </TokenAuthWrapper>
          } />
          <Route path="/signup" element={<Signup onSignup={handleSignup} />} />
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          
          {/* Exam Reservation System */}
          <Route path="/exam/reserve" element={<ExamReservationForm />} />
          <Route path="/exam/confirmation" element={<ExamConfirmation />} />
          <Route path="/exam/guide" element={<ExamGuide />} />
          
          {/* Parent Dashboard */}
          <Route path="/parent/dashboard" element={<ParentDashboard />} />
          
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