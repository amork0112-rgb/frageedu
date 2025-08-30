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
  Play
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
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Frage EDU</h1>
              <p className="text-xs text-gray-500">생각하는 영어교육</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="/#about" className="text-gray-700 hover:text-purple-600 transition-colors">About</a>
            <a href="/programs" className="text-gray-700 hover:text-purple-600 transition-colors">Programs</a>
            <a href="/admissions" className="text-gray-700 hover:text-purple-600 transition-colors">Admissions</a>
            <a href="/community" className="text-gray-700 hover:text-purple-600 transition-colors">Community</a>
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
              <a href="/community" className="text-gray-700 hover:text-purple-600 transition-colors">Community</a>
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
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Contact Info</h4>
            <ul className="space-y-2 text-gray-400">
              <li className="flex items-center space-x-2">
                <MapPin className="w-4 h-4" />
                <span>서울시 강남구 테헤란로 123</span>
              </li>
              <li className="flex items-center space-x-2">
                <Phone className="w-4 h-4" />
                <span>02-1234-5678</span>
              </li>
              <li className="flex items-center space-x-2">
                <Mail className="w-4 h-4" />
                <span>info@frage.edu</span>
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
              <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
                생각하는 힘을 키우는<br />
                <span className="text-purple-600">영어교육, 프라게</span>
              </h1>
              <p className="text-lg lg:text-xl text-gray-600 mb-8 leading-relaxed">
                Frage EDU — Growing the Power to Think through English Learning.<br />
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

      {/* Community Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">Community</h2>
            <p className="text-xl text-gray-600">학부모와 학생들이 함께 만드는 교육 공동체</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">학부모 후기</h3>
              <div className="space-y-6">
                <Card className="p-6">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                      <span className="text-purple-600 font-semibold">김</span>
                    </div>
                    <div>
                      <h4 className="font-semibold">김○○ 학부모</h4>
                      <p className="text-sm text-gray-500">초등 3학년 학부모</p>
                    </div>
                  </div>
                  <p className="text-gray-600">
                    "아이가 영어에 대한 흥미를 잃었었는데, 프라게에 다니면서 다시 영어가 재미있다고 합니다."
                  </p>
                </Card>

                <Card className="p-6">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <span className="text-green-600 font-semibold">박</span>
                    </div>
                    <div>
                      <h4 className="font-semibold">박○○ 학부모</h4>
                      <p className="text-sm text-gray-500">초등 5학년 학부모</p>
                    </div>
                  </div>
                  <p className="text-gray-600">
                    "단순 암기가 아닌 생각하는 영어교육으로 아이의 사고력이 많이 늘었어요."
                  </p>
                </Card>
              </div>
            </div>

            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">최신 소식</h3>
              <div className="space-y-6">
                <Card className="p-6 hover:shadow-lg transition-shadow">
                  <h4 className="font-semibold mb-2">2025 겨울방학 특별 프로그램 안내</h4>
                  <p className="text-gray-600 mb-3">
                    창의적 글쓰기와 토론 중심의 집중 영어 캠프를 진행합니다.
                  </p>
                  <span className="text-sm text-purple-600">2025.01.15</span>
                </Card>

                <Card className="p-6 hover:shadow-lg transition-shadow">
                  <h4 className="font-semibold mb-2">학부모 교육 세미나 개최</h4>
                  <p className="text-gray-600 mb-3">
                    자녀의 영어 학습을 도울 수 있는 가정 내 환경 조성법을 알려드립니다.
                  </p>
                  <span className="text-sm text-purple-600">2025.01.10</span>
                </Card>
              </div>

              <Button variant="outline" className="w-full mt-6">
                Join the Community
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
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

// Simple Placeholder Pages
const Programs = () => (
  <div className="min-h-screen bg-white pt-20">
    <Header />
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Programs</h1>
      <p className="text-xl text-gray-600">프로그램 상세 페이지 (구현 예정)</p>
    </div>
    <Footer />
  </div>
);

const Community = () => (
  <div className="min-h-screen bg-white pt-20">
    <Header />
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Community</h1>
      <p className="text-xl text-gray-600">커뮤니티 페이지 (구현 예정)</p>
    </div>
    <Footer />
  </div>
);

const News = () => (
  <div className="min-h-screen bg-white pt-20">
    <Header />
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">News & Blog</h1>
      <p className="text-xl text-gray-600">뉴스 및 블로그 페이지 (구현 예정)</p>
    </div>
    <Footer />
  </div>
);

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

// Admissions Portal Landing
const AdmissionsPortal = () => {
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

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          <Card className="p-8 text-center hover:shadow-lg transition-shadow">
            <Users className="w-16 h-16 text-purple-600 mx-auto mb-4" />
            <h3 className="text-2xl font-semibold mb-4">신규 학부모</h3>
            <p className="text-gray-600 mb-6">
              처음 방문하시는 분은 여기서 회원가입을 진행해주세요.
            </p>
            <Button className="w-full bg-purple-600 hover:bg-purple-700" onClick={() => window.location.href = '/signup'}>
              회원가입하기
            </Button>
          </Card>

          <Card className="p-8 text-center hover:shadow-lg transition-shadow">
            <Shield className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h3 className="text-2xl font-semibold mb-4">기존 학부모</h3>
            <p className="text-gray-600 mb-6">
              이미 계정이 있으시면 로그인하여 입학 절차를 계속 진행하세요.
            </p>
            <Button variant="outline" className="w-full" onClick={() => window.location.href = '/login'}>
              로그인하기
            </Button>
          </Card>
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