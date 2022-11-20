#include<iostream>
#include<unordered_map>
#include<set>
#include<list>
#include<string>
using namespace std;

#define fastio() ios_base::sync_with_stdio(false);cin.tie(NULL);cout.tie(NULL)
unordered_map<string, list<pair<string, float> > > ans;
unordered_map<string, float> all;
set<pair<float, string> > st;

void fun(){
   ans.clear();
   all.clear();
   st.clear();
   int e;cin>>e;
   for(int i = 0; i<e; i++){
       string u, v;
       float w;
       cin>>u>>v>>w;
       all[u] -= w;
       all[v] += w;
   }
   for(auto it: all)if(it.second != 0)st.insert({it.second, it.first});
   while(!st.empty()){
       auto lo = st.begin(), hi = prev(st.end());st.erase(lo), st.erase(hi);
       float neg = (*lo).first, pos = (*hi).first;
       string s1 = (*lo).second, s2 = (*hi).second;
       float mn = min(-neg, pos);
       neg += mn;
       pos -= mn;
       if(neg == 0 or pos == 0){
           ans[s1].push_back({s2, mn});
       }
       if(neg != 0)st.insert({neg, s1});
       if(pos != 0)st.insert({pos, s2});
   }
   int cnt = 0;
   for(auto it1: ans){
       cout<<"\n";
       cout<<it1.first<<":-> ";
       for(auto it2: ans[it1.first]){
           cout<<"[\""<<it2.first<<"\" "<<it2.second<<"]";
           if(it2 != *prev(ans[it1.first].end()))
            cout<<", ";
           cnt++;
       }
   }
   cout<<"\n"<<cnt;
}

int main(){
    fastio();
    int TC;cin>>TC;
    while(TC--)fun();
    return 0;
}

/*
TEST CASES
2

5
Atul Ankit 112
Ankit Bunty 30
Shishank Ankit 150
Bunty Shishank 3000
Atul Bunty 101

3
Rahul Ajay 100
Ajay Neha 50
Neha Rahul 40
*/
