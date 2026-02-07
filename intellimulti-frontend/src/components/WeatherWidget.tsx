import React, { useEffect, useState, useRef } from 'react';
import { Cloud, Droplets, Thermometer, MapPin, RefreshCw } from 'lucide-react';
import { Card, Spin, Typography } from 'antd';

const { Text } = Typography;

interface WeatherInfo {
  city: string;
  temperature: number;
  feels_like: number;
  weather: string;
  humidity: number;
  update_time: string;
}

export const WeatherWidget: React.FC = () => {
  const [weather, setWeather] = useState<WeatherInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const fetchedRef = useRef(false);

  const fetchWeather = async () => {
    try {
      setLoading(true);
      setError(null);
      // Using POST as defined in the backend
      const response = await fetch('http://localhost:8000/api/get_weather', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch weather data');
      }

      const data: WeatherInfo = await response.json();
      
      if (data && data.city) {
        setWeather(data);
      } else {
        setError('暂无天气数据');
      }
    } catch (err) {
      console.error('Error fetching weather:', err);
      setError('天气服务暂时不可用');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    fetchWeather();
  }, []);

  if (error) {
    return null; // Or show error state lightly
  }

  if (loading && !weather) {
    return (
      <div className="fixed top-4 right-4 z-[9999]">
        <Card className="w-64 shadow-lg border-none bg-white/5 backdrop-blur-md">
            <div className="flex justify-center py-4">
                <Spin tip="获取天气中..." size="small" />
            </div>
        </Card>
      </div>
    );
  }

  if (!weather) return null;

  return (
    <div className="fixed top-6 right-6 z-[9999] animate-fade-in pointer-events-none">
      <div className="relative group pointer-events-auto">
        {/* 科技感外发光阴影 */}
        <div className="absolute -inset-[1px] bg-gradient-to-r from-blue-600/40 to-cyan-500/40 rounded-2xl blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
        
        <div className="relative w-60 overflow-hidden rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.3)] transition-all duration-300 hover:translate-y-[-2px]">
          {/* 背景动态渐变装饰 */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/20 rounded-full blur-3xl -mr-16 -mt-16 animate-pulse"></div>
          
          <div className="p-4 flex flex-col gap-3">
            {/* 顶栏：城市与刷新 */}
            <div className="flex justify-between items-center border-b border-white/5 pb-2">
              <div className="flex items-center gap-2">
                <MapPin size={14} className="text-blue-400" />
                <span className="text-[12px] font-bold tracking-widest text-white/90 uppercase truncate max-w-[120px]">
                  {weather.city}
                </span>
              </div>
              <RefreshCw 
                size={12} 
                className={`cursor-pointer text-white/30 hover:text-blue-400 transition-all ${loading ? 'animate-spin' : 'hover:rotate-180'}`} 
                onClick={(e) => {
                  e.stopPropagation();
                  fetchWeather();
                }}
              />
            </div>

            {/* 中间：温度与图标 */}
            <div className="flex items-center justify-between px-1 py-1">
              <div className="flex flex-col">
                <div className="flex items-baseline">
                  <span className="text-4xl font-black text-white tracking-tighter drop-shadow-md">
                    {weather.temperature}
                  </span>
                  <span className="text-lg font-bold text-blue-400 ml-1">°C</span>
                </div>
                <div className="mt-1">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-blue-500/20 border border-blue-400/30 text-[10px] font-bold text-blue-200">
                    {weather.weather}
                  </span>
                </div>
              </div>
              <div className="relative flex items-center justify-center">
                <div className="absolute inset-0 bg-blue-400/20 blur-xl rounded-full"></div>
                <Cloud size={40} className="relative text-white drop-shadow-[0_0_8px_rgba(59,130,246,0.8)]" strokeWidth={1.5} />
              </div>
            </div>

            {/* 底栏：核心指标 */}
            <div className="flex items-center gap-4 pt-1">
              <div className="flex items-center gap-1.5 group/item">
                <div className="p-1 rounded-md bg-orange-500/10 border border-orange-500/20">
                  <Thermometer size={12} className="text-orange-400" />
                </div>
                <div className="flex flex-col">
                  <span className="text-[9px] text-white/40 font-bold uppercase tracking-tighter">Feels</span>
                  <span className="text-[11px] text-white/90 font-semibold">{weather.feels_like}°</span>
                </div>
              </div>
              <div className="flex items-center gap-1.5 group/item">
                <div className="p-1 rounded-md bg-blue-500/10 border border-blue-500/20">
                  <Droplets size={12} className="text-blue-400" />
                </div>
                <div className="flex flex-col">
                  <span className="text-[9px] text-white/40 font-bold uppercase tracking-tighter">Humidity</span>
                  <span className="text-[11px] text-white/90 font-semibold">{weather.humidity}%</span>
                </div>
              </div>
            </div>
            
            {/* 时间戳 - 增加可读性 */}
            <div className="flex items-center justify-end mt-1">
              <div className="h-[1px] flex-1 bg-gradient-to-r from-transparent to-white/5 mr-3"></div>
              <span className="text-[9px] text-white/20 font-mono font-medium">
                LAST UPDATE: {weather.update_time.split(' ')[1] || weather.update_time}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
