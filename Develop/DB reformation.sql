-- created by sunsky 20171230
-- modified by return0927 20171231
-- 코멘트 추가 by sunsky 20180101
--
-- int, bigint, serial, bigserial, varchar[N] 등의 data type과 그 크기에 대해서는 개발자님과 의견교환 꼭 할 것.
-- table 종류가 너무 잘게 쪼개진 것은 아닌지.. 개발자님께 문의/의논 할 것.
-- problem_table 에서 자이스토리 같은 경우를 어떻게 처리할지를 'page' column 관련해서 의논할 것.
-- student_table 만들것(기존의 user 라는 테이블에 해당할지도 모름)
-- (통상적으로 개발에서 어떤 용어를 쓰는지 모르겠습니다만) 아래와 같이 사용해 봅니다.
-- 공지 : 전체에게 보내는 메시지
-- 알림 : 특정회원 또는 몇몇의 회원에게 보내는 메시지
-- push_table (알림) 이나 notice_table (공지) 같은 것도 만들어야 할까..? 잘 모르겠음. 개발자님과 의논할 것.

CREATE TABLE curriculum (-- 교육과정상의 과목DB
  id   INT PRIMARY KEY,
  name VARCHAR(20), -- 예를 들어 미적분I , 수학(상)
  year INT            -- 개정과정 연도(출판연도가 아님)
  -- 현재과정은 2009 이고, 개정과정은 2015임.
);

-- insert into tablename 뒤의 형태
-- (수학II, 2009)
-- (미적분I, 2009)
-- (수학, 2015)
-- (수학(상), 2015)
-- (수학II, 2015) 참고로, 2009개정과정의 수학II 와는 다른 내용임.
-- 참고로, 교과서는 '수학' 으로 나오지만 참고서들은 이것을 두 학기로 잘라서 '수학(상)' 과 '수학(하)' 로 나눠서 내놓는 경우가 많음.

CREATE TABLE bookseries (-- 출판된 교재명DB
  name          VARCHAR(20) PRIMARY KEY, -- 예를 들어 일품, 블랙라벨, 2017마플수능기출
  publishername VARCHAR(20)    -- 출판사 이름
);

-- name 을 출판사에서 등록한 '공식명칭' 으로 하는 것보다는 '통상적으로 알려진 이름' 으로 하는게 좋을 듯하다.
-- 예를 들어, 공식명칭이 '수학의 정석 기본편' 이더라도 DB 및 UI 상에서는 '기본정석' 이라고 쓰는게 좋을 듯하다.
-- insert into tablename 뒤의 형태
-- (쎈, 좋은책신사고)
-- (블랙라벨, 진학사)
-- (자이스토리고3, 수경출판사)

CREATE TABLE book (-- 과목별 교재별 DB
  book_id            SERIAL PRIMARY KEY, -- 1부터 시작하며 auto increment
  currId             INT REFERENCES curriculum (id),
  bookname           VARCHAR(20) REFERENCES bookseries (name),
  year               INT, -- 책이 출판된 연도임(1판 1쇄)
  chapter_indication INT      -- child table 인 problem table 에서 'page' 가 가지는 의미를 구분함. 예를 들어,
                    -- 0:사용하지 않음 (쎈처럼 문항번호만으로 가능한 교재)
                    -- 1:page      (교과서, 블랙라벨 처럼 page 가 필요한 교재)
                    -- 2:chapter    (정석처럼 chapter를 숫자로 표기할 때)
                    -- 3:단원문자    (자이스토리처럼 chapter를 영문자로 표기할 때, 그 영문자의 ASCII code를 담는다)
);

-- 매년 개정판이 나오게 되는 기출교재들(마플, 자이스토리 등등)의 경우, bookseries 상에서는 하나로 취급하고
-- book 에서 year 가 개정판 연도에 맞춰서 새로 등록되는 것으로 하는것이 좋을 듯하다.
-- insert into tablename 뒤의 형태
-- (미적분I, 쎈, 2014)
-- (미적분I, 쎈, 2016)
-- (미적분II, 2017마플수능기출, 2016)
-- (수학II, 블랙라벨, 2013)
-- ((개정)수학II, 블랙라벨, 2018)

CREATE TABLE problem (-- 문제 DB
  problem_id BIGSERIAL PRIMARY KEY,  -- 약 200종의 book이 있고, book마다 평균적으로 1천문제가 있다고 할 경우, serial 의 범위를 벗어남.
                      -- problem 이후의 solution_video, question 등의 table 들에서도 마찬가지임.
  book_id    INT REFERENCES book (book_id),
  page       INT, -- 교재에 따라서는 page 가 아닌 chapter 등을 나타낸다.(book table 의 chapter_indication 참조)
  number     INT
);

CREATE TABLE solution_video (-- 해설동영상 DB
  problem_id BIGINT REFERENCES problem (problem_id) PRIMARY KEY,  -- 한 문제당 하나의 해설영상만 만들어진다고 가정한 것임.
                   -- 향후에 같은 문제에 대해 다른 해설이(예를 들어 다른 tutor) 만들어진다거나 할때는 DB 구조를 변경할 것.
  url        VARCHAR(160), -- 실제 해설영상으로의 링크.
  tutor      VARCHAR(20), -- 당분간은 sunsky 를 default 로 한다.(나중에 tutor가 추가될 때는 tutor table 도 만든다)
  hit        INT
);

CREATE TABLE question (-- 질문 DB
  question_id BIGSERIAL PRIMARY KEY,
  problem_id  BIGINT REFERENCES problem (problem_id),
  student_id  INT REFERENCES users(id), -- int 면 충분하겠지..? 그 이상 필요하게 되면 이미 대박임. ^__^
  q_date      DATE, -- question date
  p_date      DATE, -- processed date(해설영상 올리고 학생에게 message 보내는 등의 처리를 완료한 시점)
  status      INT, -- int 로 할지 varchar[N] 으로 할지 미정
  message     VARCHAR(100)
  -- 기타 ip 등등.. 개발자님이 내용 추가할 것들.
);

CREATE TABLE billing (-- 과금 DB(어쩌면 그냥 question table 에 price field 하나 추가해서 써도 될지도 모른다)
            -- 20171231 회의에서 나온 얘기 중에 '이벤트 등등의 이유'로 인해 user 의 point 를 올려주는 경우가 생길수 있다.
            -- 즉, question과 무관한 billing(billing 이라고 부르기도 애매한)이 생길 수 있다.
            -- 그런데 이럴 경우, question_id references question(question_id) 부분이 문제가 될 수도 있겠다.
            -- billing table 은 다시 구성해야 할지도 모르겠다는 생각도 듭니다.
  billing_id  BIGSERIAL PRIMARY KEY,
  question_id BIGINT REFERENCES question (question_id),
  b_date      DATE, -- 과금 date이며, 기본적으로는 question_table(q_date)와 같아도 문제는 안될 듯하다.
  price       INT, -- 과금 금액(또는 point)
  message     VARCHAR(100)
);

CREATE TABLE payment (-- 결제 DB : user들이 결제한 사항에 대한 기록. 즉, 온풀서비스의 client 나 server 와는 무관한 내용이라고 생각됨.
            -- 단지 서비스 관리차원(back office라고 하나요?)에서 필요한 DB 임.
  payment_id BIGSERIAL PRIMARY KEY,    -- 만명의 학생이 매월 1회씩 결제한다고 치고 1년이면 12만. 미리 여유있게 잡아놓은 것임.
  student_id INT REFERENCES ssolve.public."User"(id),
  p_date     DATE, -- payment date
  price      INT, -- 결제 금액
  method     INT         -- 1:현금(계좌이체) 2:카드 11:쿠폰(예를 들어 와디즈쿠폰) 12:혜택(보너스?)
);