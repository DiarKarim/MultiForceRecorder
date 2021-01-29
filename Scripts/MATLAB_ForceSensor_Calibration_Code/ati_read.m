function d = ati_read(fname)
%%read ati 6DoF calibration file and export in a matrix
fid = fopen(fname);
t=1;
j=1;
tline = fgetl(fid);
while ischar(tline)
    tline = fgetl(fid);
    if t>=8&&t<=14
        a = strfind(tline,'"');
        d(j,1:6) = str2num(tline(a(3)+1:a(4)-1));
        d(j,7) = str2num(tline(a(end-1)+1:a(end)-1));
        if j ==7
            b = transpose(reshape(a,2,length(a)/2));
            d(j,1) =  str2num(tline(b(1,1)+1:b(1,2)-1));
            d(j,2) =  str2num(tline(b(2,1)+1:b(2,2)-1));
            d(j,3) =  str2num(tline(b(3,1)+1:b(3,2)-1));
            d(j,4) =  str2num(tline(b(4,1)+1:b(4,2)-1));
            d(j,5) =  str2num(tline(b(5,1)+1:b(5,2)-1));
            d(j,6) =  str2num(tline(b(6,1)+1:b(6,2)-1));
            d(j,7) =  0;
        end
        j = j+1;
    end
    t = t+1;
end
fclose(fid);
end