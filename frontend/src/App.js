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
import { CheckCircle, Clock, FileText, BookOpen, ClipboardList, Users, Info, Eye } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const useAuth = () => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchProfile();
    }
  }, [token]);

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API}/profile`);
      setUser(response.data);
    } catch (error) {
      logout();
    }
  };

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

// Signup Component
const Signup = ({ onSignup }) => {
  const [formData, setFormData] = useState({
    email: '',
    phone: '',
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-indigo-900">Frage EDU</CardTitle>
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
            
            <Button type="submit" className="w-full" disabled={loading || !formData.terms_accepted}>
              {loading ? "가입 중..." : "가입하기"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

// Dashboard Component
const Dashboard = ({ user }) => {
  const [admissionData, setAdmissionData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('id');
    const tokenToUse = tokenFromUrl || user?.household_token;
    
    if (tokenToUse) {
      fetchAdmissionData(tokenToUse);
    }
  }, [user]);

  const fetchAdmissionData = async (token) => {
    try {
      const response = await axios.get(`${API}/admission/${token}`);
      setAdmissionData(response.data);
    } catch (error) {
      console.error('Failed to fetch admission data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    return status === 'completed' ? (
      <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
        <CheckCircle className="w-3 h-3 mr-1" />
        완료
      </Badge>
    ) : (
      <Badge variant="secondary">
        <Clock className="w-3 h-3 mr-1" />
        대기중
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">입학 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  const token = new URLSearchParams(window.location.search).get('id') || user?.household_token;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Users className="w-8 h-8 text-indigo-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Frage EDU</h1>
                <p className="text-sm text-gray-500">입학 준비 포털</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">{user?.email}</p>
              <p className="text-xs text-gray-400">토큰: {token?.slice(0, 8)}...</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">입학 진행 상황</h2>
          <p className="text-gray-600">아래 단계들을 순서대로 완료해 주세요.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Consent Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" 
                onClick={() => window.location.href = `/consent?id=${token}`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <CardTitle className="text-lg">동의서</CardTitle>
                </div>
                {admissionData && getStatusBadge(admissionData.consent_status)}
              </div>
              <CardDescription>
                학교 규정 및 개인정보처리방침 동의
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                입학을 위한 필수 동의서를 검토하고 서명해주세요.
              </p>
            </CardContent>
          </Card>

          {/* Forms Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => window.location.href = `/form?id=${token}`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <ClipboardList className="w-5 h-5 text-green-600" />
                  <CardTitle className="text-lg">신청서</CardTitle>
                </div>
                {admissionData && getStatusBadge(admissionData.forms_status)}
              </div>
              <CardDescription>
                입학신청서, 설문조사, 우유급식, 방과후
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                학생 정보와 희망 프로그램을 입력해주세요.
              </p>
            </CardContent>
          </Card>

          {/* Guides Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => window.location.href = `/guide?id=${token}`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <BookOpen className="w-5 h-5 text-purple-600" />
                  <CardTitle className="text-lg">안내사항</CardTitle>
                </div>
                {admissionData && getStatusBadge(admissionData.guides_status)}
              </div>
              <CardDescription>
                버스, 숙제, 방과후, 고급반, 커뮤니티 안내
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                학교생활에 필요한 중요한 안내사항들을 확인하세요.
              </p>
            </CardContent>
          </Card>

          {/* Checklist Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => window.location.href = `/checklist?id=${token}`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-orange-600" />
                  <CardTitle className="text-lg">준비 체크리스트</CardTitle>
                </div>
                {admissionData && getStatusBadge(admissionData.checklist_status)}
              </div>
              <CardDescription>
                입학 전 필수 준비물 확인
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                입학 전 준비해야 할 모든 항목들을 체크하세요.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Progress Summary */}
        {admissionData && (
          <Card className="mt-8 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-lg text-center">전체 진행률</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-4 gap-4 text-center">
                <div>
                  <div className={`w-16 h-16 rounded-full mx-auto mb-2 flex items-center justify-center ${
                    admissionData.consent_status === 'completed' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
                  }`}>
                    <FileText className="w-8 h-8" />
                  </div>
                  <p className="text-xs font-medium">동의서</p>
                </div>
                <div>
                  <div className={`w-16 h-16 rounded-full mx-auto mb-2 flex items-center justify-center ${
                    admissionData.forms_status === 'completed' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
                  }`}>
                    <ClipboardList className="w-8 h-8" />
                  </div>
                  <p className="text-xs font-medium">신청서</p>
                </div>
                <div>
                  <div className={`w-16 h-16 rounded-full mx-auto mb-2 flex items-center justify-center ${
                    admissionData.guides_status === 'completed' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
                  }`}>
                    <BookOpen className="w-8 h-8" />
                  </div>
                  <p className="text-xs font-medium">안내사항</p>
                </div>
                <div>
                  <div className={`w-16 h-16 rounded-full mx-auto mb-2 flex items-center justify-center ${
                    admissionData.checklist_status === 'completed' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
                  }`}>
                    <CheckCircle className="w-8 h-8" />
                  </div>
                  <p className="text-xs font-medium">체크리스트</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

// Consent Details Data
const consentDetails = {
  regulation: {
    title: "학교 규정 동의",
    content: `
**학교 운영 규정 및 교육 방침**

1. **출결 관리**
   - 등교 시간: 오전 8:30까지
   - 지각 3회는 결석 1회로 처리
   - 결석 시 반드시 전날까지 연락

2. **학습 지도**
   - 숙제는 매일 확인하여 제출
   - 학부모 상담은 월 1회 실시
   - 성적 평가는 다면평가로 진행

3. **생활 지도**
   - 교내에서는 실내화 착용 의무
   - 전자기기 반입 금지
   - 폭력이나 괴롭힘 발생 시 즉시 조치

4. **안전 관리**
   - 학교 안전 규칙 준수
   - 위험 행동 금지
   - 안전사고 발생 시 즉시 보호자 연락
    `
  },
  privacy: {
    title: "개인정보처리방침 동의",
    content: `
**개인정보 수집 및 이용에 관한 동의**

1. **수집하는 개인정보**
   - 학생: 성명, 생년월일, 주소, 연락처
   - 학부모: 성명, 연락처, 이메일, 직업
   - 학습 관련: 성적, 출결, 특기사항

2. **개인정보 이용 목적**
   - 학사 운영 및 교육 서비스 제공
   - 학부모 연락 및 상담
   - 학교 행사 및 프로그램 안내
   - 응급상황 발생 시 연락

3. **개인정보 보유 기간**
   - 재학 기간 + 졸업 후 5년
   - 법령에 따른 보존 의무 기간 준수

4. **개인정보 제3자 제공**
   - 교육청, 보건소 등 법령에 따른 제공
   - 학부모 동의 시에만 외부 기관 제공

5. **개인정보 처리 위탁**
   - 급식업체, 통학버스 운영업체
   - 위탁계약 시 안전성 확보 조치
    `
  },
  photo: {
    title: "사진 촬영 및 활용 동의",
    content: `
**학교 활동 사진 촬영 및 사용에 관한 동의**

1. **촬영 범위**
   - 교실 수업 활동
   - 학교 행사 및 체험학습
   - 방과후 프로그램 활동
   - 급식 및 휴식 시간

2. **사용 목적**
   - 학교 홈페이지 및 소식지 게재
   - 학교 홍보 자료 제작
   - 교육활동 기록 및 보관
   - SNS 및 언론 보도 자료

3. **사용 기간**
   - 촬영일로부터 3년간
   - 졸업 앨범 등 기념품: 영구 보관

4. **개인정보 보호**
   - 학생 성명 등 개인식별정보 제외
   - 부적절한 용도 사용 금지
   - 보호자 요청 시 삭제 조치

5. **동의 철회**
   - 언제든지 동의 철회 가능
   - 철회 시 해당 사진 사용 중단
    `
  },
  medical: {
    title: "응급 의료 동의",
    content: `
**응급상황 시 의료 처치에 관한 동의**

1. **응급상황 범위**
   - 외상: 타박상, 찰과상, 골절 등
   - 질병: 발열, 복통, 두통 등
   - 알레르기 반응
   - 기타 응급을 요하는 상황

2. **응급처치 절차**
   - 1차: 학교 보건교사 응급처치
   - 2차: 인근 병원 이송 및 치료
   - 3차: 보호자 연락 및 상황 설명

3. **의료기관 이용**
   - 인근 지정 병원 우선 이용
   - 응급실 이용 시 즉시 보호자 연락
   - 치료비는 보호자 부담

4. **의료진과의 소통**
   - 학생 상태 및 알레르기 정보 전달
   - 치료 과정 및 결과 보고
   - 후속 조치 계획 수립

5. **보험 및 책임**
   - 학교안전공제회 보험 적용
   - 학교 과실 시 손해배상
   - 불가항력 사고는 면책
    `
  }
};

// Consent Page
const ConsentPage = () => {
  const [formData, setFormData] = useState({
    regulation_agreed: false,
    privacy_agreed: false,
    photo_consent: false,
    medical_consent: false
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const token = new URLSearchParams(window.location.search).get('id');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.put(`${API}/admission/${token}/consent`, formData);
      setSuccess(true);
      setTimeout(() => {
        window.location.href = `/dashboard?id=${token}`;
      }, 2000);
    } catch (error) {
      console.error('Failed to update consent:', error);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <Card className="w-full max-w-md text-center">
          <CardContent className="pt-6">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">동의 완료!</h2>
            <p className="text-gray-600">대시보드로 이동합니다...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const ConsentItem = ({ id, title, description, checked, onChange, detailKey }) => (
    <div className="flex items-start space-x-3 p-4 rounded-lg border hover:bg-gray-50">
      <Checkbox
        id={id}
        checked={checked}
        onCheckedChange={onChange}
        className="mt-1"
      />
      <div className="flex-1">
        <div className="flex items-center justify-between">
          <Label htmlFor={id} className="font-medium text-base cursor-pointer">{title}</Label>
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-800">
                <Eye className="w-4 h-4 mr-1" />
                자세히 보기
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-xl">{consentDetails[detailKey].title}</DialogTitle>
                <DialogDescription className="text-sm text-gray-600">
                  상세 내용을 확인하신 후 동의해주세요.
                </DialogDescription>
              </DialogHeader>
              <div className="mt-4">
                <div className="prose prose-sm max-w-none">
                  {consentDetails[detailKey].content.split('\n').map((line, index) => {
                    if (line.trim() === '') return <br key={index} />;
                    if (line.startsWith('**') && line.endsWith('**')) {
                      return <h3 key={index} className="font-bold text-gray-900 mt-4 mb-2">{line.slice(2, -2)}</h3>;
                    }
                    if (line.trim().startsWith('-')) {
                      return <li key={index} className="ml-4 mb-1">{line.trim().slice(1).trim()}</li>;
                    }
                    if (line.match(/^\d+\./)) {
                      return <h4 key={index} className="font-semibold text-gray-800 mt-3 mb-1">{line}</h4>;
                    }
                    return <p key={index} className="mb-2 text-gray-700">{line}</p>;
                  })}
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">동의서</CardTitle>
            <CardDescription>
              각 항목의 상세 내용을 확인하신 후 동의해주세요. 자세히 보기 버튼을 클릭하면 상세 내용을 확인할 수 있습니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <ConsentItem
                id="regulation"
                title="학교 규정 동의"
                description="학교 운영 규정 및 교육 방침에 동의합니다."
                checked={formData.regulation_agreed}
                onChange={(checked) => setFormData({...formData, regulation_agreed: checked})}
                detailKey="regulation"
              />

              <ConsentItem
                id="privacy"
                title="개인정보처리방침 동의"
                description="개인정보 수집, 이용, 제공에 대한 방침에 동의합니다."
                checked={formData.privacy_agreed}
                onChange={(checked) => setFormData({...formData, privacy_agreed: checked})}
                detailKey="privacy"
              />

              <ConsentItem
                id="photo"
                title="사진 촬영 및 활용 동의"
                description="학교 활동 사진 촬영 및 홍보 목적 사용에 동의합니다."
                checked={formData.photo_consent}
                onChange={(checked) => setFormData({...formData, photo_consent: checked})}
                detailKey="photo"
              />

              <ConsentItem
                id="medical"
                title="응급 의료 동의"
                description="응급상황 시 필요한 의료 처치에 대해 동의합니다."
                checked={formData.medical_consent}
                onChange={(checked) => setFormData({...formData, medical_consent: checked})}
                detailKey="medical"
              />

              <div className="flex space-x-3 pt-6">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => window.location.href = `/dashboard?id=${token}`}
                  className="flex-1"
                >
                  뒤로가기
                </Button>
                <Button 
                  type="submit" 
                  className="flex-1"
                  disabled={loading || !Object.values(formData).every(Boolean)}
                >
                  {loading ? "저장 중..." : "동의하고 계속"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Forms Page
const FormsPage = () => {
  const [formData, setFormData] = useState({
    student_name: '',
    birth_date: '',
    parent_name: '',
    emergency_contact: '',
    allergies: '',
    milk_program: false,
    afterschool_program: ''
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const token = new URLSearchParams(window.location.search).get('id');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.put(`${API}/admission/${token}/forms`, formData);
      setSuccess(true);
      setTimeout(() => {
        window.location.href = `/dashboard?id=${token}`;
      }, 2000);
    } catch (error) {
      console.error('Failed to update forms:', error);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <Card className="w-full max-w-md text-center">
          <CardContent className="pt-6">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">신청서 제출 완료!</h2>
            <p className="text-gray-600">대시보드로 이동합니다...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">입학 신청서</CardTitle>
            <CardDescription>
              학생 정보와 희망 프로그램을 입력해주세요.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="student_name">학생 이름</Label>
                  <Input
                    id="student_name"
                    value={formData.student_name}
                    onChange={(e) => setFormData({...formData, student_name: e.target.value})}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="birth_date">생년월일</Label>
                  <Input
                    id="birth_date"
                    type="date"
                    value={formData.birth_date}
                    onChange={(e) => setFormData({...formData, birth_date: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="parent_name">학부모 이름</Label>
                <Input
                  id="parent_name"
                  value={formData.parent_name}
                  onChange={(e) => setFormData({...formData, parent_name: e.target.value})}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="emergency_contact">비상 연락처</Label>
                <Input
                  id="emergency_contact"
                  type="tel"
                  placeholder="010-1234-5678"
                  value={formData.emergency_contact}
                  onChange={(e) => setFormData({...formData, emergency_contact: e.target.value})}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="allergies">알레르기 정보</Label>
                <Textarea
                  id="allergies"
                  placeholder="알레르기가 있다면 자세히 기록해주세요"
                  value={formData.allergies}
                  onChange={(e) => setFormData({...formData, allergies: e.target.value})}
                />
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="milk_program"
                  checked={formData.milk_program}
                  onCheckedChange={(checked) => setFormData({...formData, milk_program: checked})}
                />
                <Label htmlFor="milk_program">우유급식 신청</Label>
              </div>

              <div className="space-y-2">
                <Label htmlFor="afterschool_program">방과후 프로그램</Label>
                <Select value={formData.afterschool_program} onValueChange={(value) => setFormData({...formData, afterschool_program: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="프로그램을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">신청안함</SelectItem>
                    <SelectItem value="sports">체육 프로그램</SelectItem>
                    <SelectItem value="art">미술 프로그램</SelectItem>
                    <SelectItem value="music">음악 프로그램</SelectItem>
                    <SelectItem value="coding">코딩 프로그램</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex space-x-3">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => window.location.href = `/dashboard?id=${token}`}
                  className="flex-1"
                >
                  뒤로가기
                </Button>
                <Button type="submit" className="flex-1" disabled={loading}>
                  {loading ? "제출 중..." : "신청서 제출"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Guide Page
const GuidePage = () => {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const token = new URLSearchParams(window.location.search).get('id');

  const markAsViewed = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/admission/${token}/guides`);
      setSuccess(true);
      setTimeout(() => {
        window.location.href = `/dashboard?id=${token}`;
      }, 2000);
    } catch (error) {
      console.error('Failed to mark guides as viewed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <Card className="w-full max-w-md text-center">
          <CardContent className="pt-6">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">안내사항 확인 완료!</h2>
            <p className="text-gray-600">대시보드로 이동합니다...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">학교생활 안내사항</CardTitle>
            <CardDescription>
              중요한 안내사항들을 꼼꼼히 읽어보세요.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Bus Guide */}
            <div>
              <h3 className="text-lg font-semibold mb-3 text-blue-900">🚌 통학버스 안내</h3>
              <div className="bg-blue-50 p-4 rounded-lg">
                <ul className="space-y-2 text-sm">
                  <li>• 운행시간: 오전 7:30 ~ 오후 6:00</li>
                  <li>• 정류장에서 10분 전 대기해주세요</li>
                  <li>• 버스카드는 입학 후 배부됩니다</li>
                  <li>• 결석 시 반드시 미리 연락주세요</li>
                </ul>
              </div>
            </div>

            {/* Homework Guide */}
            <div>
              <h3 className="text-lg font-semibold mb-3 text-green-900">📚 숙제 및 학습 안내</h3>
              <div className="bg-green-50 p-4 rounded-lg">
                <ul className="space-y-2 text-sm">
                  <li>• 매일 알림장을 확인해주세요</li>
                  <li>• 숙제는 다음날 오전 9시까지 제출</li>
                  <li>• 독서록은 주 2회 이상 작성</li>
                  <li>• 학습 상담은 매월 둘째 주 진행</li>
                </ul>
              </div>
            </div>

            {/* Afterschool Guide */}
            <div>
              <h3 className="text-lg font-semibold mb-3 text-purple-900">🎨 방과후 프로그램 안내</h3>
              <div className="bg-purple-50 p-4 rounded-lg">
                <ul className="space-y-2 text-sm">
                  <li>• 프로그램 시간: 오후 2:00 ~ 4:00</li>
                  <li>• 월별 프로그램 변경 가능</li>
                  <li>• 재료비는 별도 안내</li>
                  <li>• 발표회는 학기말 진행</li>
                </ul>
              </div>
            </div>

            {/* Advanced Program */}
            <div>
              <h3 className="text-lg font-semibold mb-3 text-orange-900">🏆 고급반 프로그램</h3>
              <div className="bg-orange-50 p-4 rounded-lg">
                <ul className="space-y-2 text-sm">
                  <li>• 대상: 학업 성취도 상위 20%</li>
                  <li>• 심화 학습 및 프로젝트 수업</li>
                  <li>• 월 1회 특별 활동</li>
                  <li>• 별도 선발 시험 있음</li>
                </ul>
              </div>
            </div>

            {/* Community Guide */}
            <div>
              <h3 className="text-lg font-semibold mb-3 text-indigo-900">👥 학부모 커뮤니티</h3>
              <div className="bg-indigo-50 p-4 rounded-lg">
                <ul className="space-y-2 text-sm">
                  <li>• 학급 단위 온라인 소통</li>
                  <li>• 월 1회 학부모 모임</li>
                  <li>• 학교 행사 자원봉사 참여</li>
                  <li>• 교육 정보 공유</li>
                </ul>
              </div>
            </div>

            <div className="flex space-x-3 pt-6">
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => window.location.href = `/dashboard?id=${token}`}
                className="flex-1"
              >
                뒤로가기
              </Button>
              <Button onClick={markAsViewed} className="flex-1" disabled={loading}>
                {loading ? "처리 중..." : "확인 완료"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Checklist Page
const ChecklistPage = () => {
  const [checklist, setChecklist] = useState([
    { id: 1, text: '학용품 준비 (연필, 지우개, 공책)', checked: false },
    { id: 2, text: '실내화 구입', checked: false },
    { id: 3, text: '체육복 준비', checked: false },
    { id: 4, text: '개인 물병 준비', checked: false },
    { id: 5, text: '건강검진 서류 제출', checked: false },
    { id: 6, text: '예방접종 증명서 제출', checked: false },
    { id: 7, text: '통학 방법 확정', checked: false },
    { id: 8, text: '비상연락망 등록', checked: false }
  ]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const token = new URLSearchParams(window.location.search).get('id');

  const toggleItem = (id) => {
    setChecklist(checklist.map(item =>
      item.id === id ? { ...item, checked: !item.checked } : item
    ));
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/admission/${token}/checklist`, { items: checklist });
      setSuccess(true);
      setTimeout(() => {
        window.location.href = `/dashboard?id=${token}`;
      }, 2000);
    } catch (error) {
      console.error('Failed to update checklist:', error);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <Card className="w-full max-w-md text-center">
          <CardContent className="pt-6">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">체크리스트 저장 완료!</h2>
            <p className="text-gray-600">대시보드로 이동합니다...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const completedCount = checklist.filter(item => item.checked).length;
  const progressPercentage = (completedCount / checklist.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">입학 준비 체크리스트</CardTitle>
            <CardDescription>
              입학 전 필요한 준비물들을 체크해주세요.
            </CardDescription>
            <div className="mt-4">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>진행률</span>
                <span>{completedCount}/{checklist.length}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {checklist.map((item) => (
                <div key={item.id} className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-gray-50">
                  <Checkbox
                    id={`item-${item.id}`}
                    checked={item.checked}
                    onCheckedChange={() => toggleItem(item.id)}
                  />
                  <Label 
                    htmlFor={`item-${item.id}`} 
                    className={`flex-1 cursor-pointer ${item.checked ? 'line-through text-gray-500' : ''}`}
                  >
                    {item.text}
                  </Label>
                  {item.checked && <CheckCircle className="w-5 h-5 text-green-600" />}
                </div>
              ))}
            </div>

            <div className="flex space-x-3 pt-6">
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => window.location.href = `/dashboard?id=${token}`}
                className="flex-1"
              >
                뒤로가기
              </Button>
              <Button onClick={handleSubmit} className="flex-1" disabled={loading}>
                {loading ? "저장 중..." : "저장하기"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Token Auth Helper - handles both JWT tokens and URL tokens
const TokenAuthWrapper = ({ children }) => {
  const urlParams = new URLSearchParams(window.location.search);
  const tokenFromUrl = urlParams.get('id');
  
  // Allow access if user has JWT token OR valid URL token
  const { user, token } = useAuth();
  const hasAccess = token || tokenFromUrl;
  
  if (!hasAccess) {
    return <Navigate to="/signup" />;
  }
  
  return children;
};

// Main App
function App() {
  const { user, token, login, logout } = useAuth();
  const [isSignup, setIsSignup] = useState(false);

  const handleSignup = (newToken, userData, household_token) => {
    login(newToken, userData);
    // Redirect to dashboard with token
    window.location.href = `/dashboard?id=${household_token}`;
  };

  const handleLogin = (newToken, userData, household_token) => {
    login(newToken, userData);
    // Redirect to dashboard with token
    window.location.href = `/dashboard?id=${household_token}`;
  };

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            token ? <Navigate to="/dashboard" /> : <Signup onSignup={handleSignup} />
          } />
          <Route path="/signup" element={<Signup onSignup={handleSignup} />} />
          <Route path="/dashboard" element={
            <TokenAuthWrapper>
              <Dashboard user={user} />
            </TokenAuthWrapper>
          } />
          <Route path="/consent" element={
            <TokenAuthWrapper>
              <ConsentPage />
            </TokenAuthWrapper>
          } />
          <Route path="/form" element={
            <TokenAuthWrapper>
              <FormsPage />
            </TokenAuthWrapper>
          } />
          <Route path="/guide" element={
            <TokenAuthWrapper>
              <GuidePage />
            </TokenAuthWrapper>
          } />
          <Route path="/checklist" element={
            <TokenAuthWrapper>
              <ChecklistPage />
            </TokenAuthWrapper>
          } />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;